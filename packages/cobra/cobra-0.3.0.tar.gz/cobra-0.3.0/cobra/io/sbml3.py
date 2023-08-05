from collections import defaultdict
from warnings import warn

import sympy
from decimal import Decimal

from .. import Metabolite, Reaction, DictList, Formula, Model

# import xml parsing libraries
from xml.dom import minidom  # only used for prettyprinting
try:
    from lxml.etree import parse, Element, SubElement, tostring, \
        register_namespace
    _with_lxml = True
except ImportError:
    from xml.etree.cElementTree import parse, Element, SubElement, tostring, \
        register_namespace
    _with_lxml = False

# deal with namespaces
ns = {"fbc": "http://www.sbml.org/sbml/level3/version1/fbc/version1",
      "sbml": "http://www.sbml.org/sbml/level3/version1/core"}
for key in ns:
    register_namespace(key, ns[key])

# XPATH query wrappers
fbc_prefix = "{" + ns["fbc"] + "}"
sbml_prefix = "{" + ns["sbml"] + "}"


def ns_query(query):
    """replace prefixes with namespcae"""
    return query.replace("fbc:", fbc_prefix).replace("sbml:", sbml_prefix)


def get_ns_attribute(tag, attribute, type=lambda x: x):
    attribute = ns_query(attribute)
    value = tag.get(attribute)
    return type(value) if value is not None else None


def set_ns_attribute(xml, attribute_name, value):
    xml.set(ns_query(attribute_name), value)


# string utility functions
def clip(string, prefix):
    """clips a prefix from the beginning of a string if it exists

    >>> clip("R_pgi", "R_")
    "pgi"

    """
    return string[len(prefix):] if string.startswith(prefix) else string


def strnum(number):
    """Utility function to convert a number to a string"""
    if isinstance(number, (Decimal, sympy.Basic, str)):
        return str(number)
    s = "%.15g" % number
    return s.rstrip(".")


or_tag = ns_query("fbc:or")
and_tag = ns_query("fbc:and")
gene_tag = ns_query("fbc:gene")


def process_gpr(sub_xml):
    """recursively convert gpr xml to a gpr string"""
    if sub_xml.tag == or_tag:
        return "( " + ' or '.join(process_gpr(i) for i in sub_xml) + " )"
    elif sub_xml.tag == ns_query("fbc:and"):
        return "( " + ' and '.join(process_gpr(i) for i in sub_xml) + " )"
    elif sub_xml.tag == gene_tag:
        return sub_xml.get("reference")
    else:
        raise Exception("unsupported tag " + sub_xml.tag)


def construct_gpr_xml(parent, expression):
    """create gpr xml under parent node"""
    if isinstance(expression, sympy.And):
        and_elem = SubElement(parent, "and")
        for arg in expression.args:
            construct_gpr_xml(and_elem, arg)
    elif isinstance(expression, sympy.Or):
        or_elem = SubElement(parent, "or")
        for arg in expression.args:
            construct_gpr_xml(or_elem, arg)
    elif isinstance(expression, sympy.Symbol):
        SubElement(parent, "gene",
                   reference=str(expression).replace(".", "__COBRA_TMP_DOT__"))
    else:
        raise Exception("unable to parse " + repr(expression))


def metabolite_from_species(species):
    """create a metabolite from an sbml species"""
    met = Metabolite(clip(species.get("id"), "M_"))
    met.name = species.get("name")
    met.compartment = species.get("compartment")
    met.charge = get_ns_attribute(species, "fbc:charge", int)
    met.formula = get_ns_attribute(species, "fbc:chemicalFormula", Formula)
    return met


def parse_xml_into_model(xml, number=float):
    xml_model = xml.find(ns_query("sbml:model"))
    model = Model()
    model.id = get_ns_attribute(xml_model, "id")

    met_xpath = ns_query(
        "sbml:listOfSpecies/sbml:species[@boundaryCondition='%s']")
    model.add_metabolites(metabolite_from_species(i)
                          for i in xml_model.findall(met_xpath % 'false'))
    boundary_metabolites = {clip(i.get("id"), "M_")
                            for i in xml_model.findall(met_xpath % 'true')}

    fbc_bounds = {}
    for fbc_bound in xml_model.findall(
            ns_query("fbc:listOfFluxBounds/fbc:fluxBound")):
        reaction_id = clip(get_ns_attribute(fbc_bound, "fbc:reaction"), "R_")
        if reaction_id not in fbc_bounds:
            fbc_bounds[reaction_id] = {}
        bound_type = get_ns_attribute(fbc_bound, "fbc:operation")
        fbc_bounds[reaction_id][bound_type] = \
            number(get_ns_attribute(fbc_bound, "fbc:value"))

    reactions = []
    for sbml_reaction in xml_model.findall(
            ns_query("sbml:listOfReactions/sbml:reaction")):
        reaction = Reaction(clip(sbml_reaction.get("id"), "R_"))
        reaction.name = sbml_reaction.get("name")
        if reaction.id in fbc_bounds:
            # todo: handle infinity
            bounds = fbc_bounds[reaction.id]
            if "equal" in bounds:
                reaction.lower_bound = reaction.upper_bound = bounds["equal"]
            if "greaterEqual" in bounds:
                reaction.lower_bound = bounds["greaterEqual"]
            if "lessEqual" in bounds:
                reaction.upper_bound = bounds["lessEqual"]
        reactions.append(reaction)

        stoichiometry = defaultdict(lambda: 0)
        for species_reference in sbml_reaction.findall(
                ns_query("sbml:listOfReactants/sbml:speciesReference")):
            met_name = clip(species_reference.get("species"), "M_")
            stoichiometry[met_name] -= \
                number(species_reference.get("stoichiometry"))
        for species_reference in sbml_reaction.findall(
                ns_query("sbml:listOfProducts/sbml:speciesReference")):
            met_name = clip(species_reference.get("species"), "M_")
            stoichiometry[met_name] += \
                number(species_reference.get("stoichiometry"))
        # needs to have keys of metabolite objects, not ids
        object_stoichiometry = {}
        for met_id in stoichiometry:
            if met_id in boundary_metabolites:
                continue
            try:
                metabolite = model.metabolites.get_by_id(met_id)
            except KeyError:
                warn("ignoring unknown metabolite '%s' in %s" %
                     (met_id, repr(reaction)))
                continue
            object_stoichiometry[metabolite] = stoichiometry[met_id]
        reaction.add_metabolites(object_stoichiometry)
    model.add_reactions(reactions)
    # objective coefficients
    obj_list = xml_model.find(ns_query("fbc:listOfObjectives"))
    target_objective = get_ns_attribute(obj_list, "fbc:activeObjective")
    obj_query = ("fbc:objective[@fbc:id='%s']/"
                 "fbc:listOfFluxObjectives/"
                 "fbc:fluxObjective") % target_objective
    for sbml_objective in obj_list.findall(ns_query(obj_query)):
        rxn_id = clip(get_ns_attribute(sbml_objective, "fbc:reaction"), "R_")
        model.reactions.get_by_id(rxn_id).objective_coefficient = \
            number(get_ns_attribute(sbml_objective, "fbc:coefficient"))

    # gene reaction rules
    gpr_xp = "sbml:annotation/fbc:listOfGeneAssociations/fbc:geneAssociation"
    for gpr_xml in xml_model.findall(ns_query(gpr_xp)):
        if len(gpr_xml) != 1:
            warn("ignoring this gpr entry")
        reaction_id = clip(gpr_xml.get("reaction"), "R_")
        reaction = model.reactions.get_by_id(reaction_id)
        gpr = process_gpr(gpr_xml[0])
        # remove outside parenthesis, if any
        if gpr.startswith("(") and gpr.endswith(")"):
            gpr = gpr[1:-1].strip()
        reaction.gene_reaction_rule = gpr

    return model


def model_to_xml(cobra_model):
    xml = Element("sbml", xmlns=ns["sbml"], level="3", version="1")
    xml.set(ns_query("fbc:required"), "false")
    xml_model = SubElement(xml, "model")
    if cobra_model.id is not None:
        xml_model.set("id", cobra_model.id)
    flux_bound_list = SubElement(xml_model, ns_query("fbc:listOfFluxBounds"))
    objectives_list_tmp = SubElement(xml_model,
                                     ns_query("fbc:listOfObjectives"))
    objectives_list_tmp.set(ns_query("fbc:activeObjective"), "obj")
    objectives_list_tmp = SubElement(objectives_list_tmp,
                                     ns_query("fbc:objective"))
    objectives_list_tmp.set(ns_query("fbc:id"), "obj")
    objectives_list_tmp.set(ns_query("fbc:type"), "maximize")
    flux_objectives_list = SubElement(objectives_list_tmp,
                                      ns_query("fbc:listOfFluxObjectives"))

    # add in compartments
    compartmenst_list = SubElement(xml_model, "listOfCompartments")
    compartments = cobra_model.compartments
    for compartment, name in compartments.items():
        SubElement(compartmenst_list, "compartment", id=compartment, name=name,
                   constant="true")

    # add in metabolites
    species_list = SubElement(xml_model, "listOfSpecies")
    # Useless required SBML params
    extra_attributes = {"constant": "false", "boundaryCondition": "false",
                        "hasOnlySubstanceUnits": "false",
                        "initialAmount": "NaN"}
    for met in cobra_model.metabolites:
        species = SubElement(species_list, "species")
        attributes = species.attrib
        attributes["id"] = "M_" + met.id
        attributes[ns_query("fbc:charge")] = str(met.charge)
        attributes[ns_query("fbc:chemicalFormula")] = str(met.formula)
        attributes["name"] = met.name
        attributes["compartment"] = met.compartment
        attributes.update(extra_attributes)

    # add in reactions
    reactions_list = SubElement(xml_model, "listOfReactions")
    for reaction in cobra_model.reactions:
        sbml_reaction = SubElement(reactions_list, "reaction")
        attributes = sbml_reaction.attrib
        id = "R_" + reaction.id
        attributes["id"] = id
        attributes["name"] = reaction.name
        # Useless required SBML params
        attributes["fast"] = "false"
        attributes["reversible"] = str(reaction.lower_bound <= 0).lower()
        # add in bounds
        lb = SubElement(flux_bound_list, ns_query("fbc:fluxBound"))
        set_ns_attribute(lb, "fbc:reaction", id)
        set_ns_attribute(lb, "fbc:value", strnum(reaction.lower_bound))
        set_ns_attribute(lb, "fbc:operation", "greaterEqual")
        ub = SubElement(flux_bound_list, ns_query("fbc:fluxBound"))
        set_ns_attribute(ub, "fbc:reaction", id)
        set_ns_attribute(ub, "fbc:value", strnum(reaction.upper_bound))
        set_ns_attribute(ub, "fbc:operation", "lessEqual")
        # objective coefficient
        if reaction.objective_coefficient != 0:
            objective = SubElement(flux_objectives_list,
                                   ns_query("fbc:fluxObjective"))
            set_ns_attribute(objective, "fbc:reaction", id)
            set_ns_attribute(objective, "fbc:coefficient",
                             strnum(reaction.objective_coefficient))

        # stoichiometry
        reactants = {}
        products = {}
        for metabolite, stoichiomety in reaction._metabolites.items():
            met_id = "M_" + metabolite.id
            if stoichiomety > 0:
                products[met_id] = strnum(stoichiomety)
            else:
                reactants[met_id] = strnum(-stoichiomety)
        if len(reactants) > 0:
            reactant_list = SubElement(sbml_reaction, "listOfReactants")
            for met_id, stoichiomety in reactants.items():
                SubElement(reactant_list, "speciesReference", species=met_id,
                           stoichiometry=stoichiomety, constant="true")
        if len(products) > 0:
            product_list = SubElement(sbml_reaction, "listOfProducts")
            for met_id, stoichiomety in products.items():
                SubElement(product_list, "speciesReference", species=met_id,
                           stoichiometry=stoichiomety, constant="true")

    # gene reaction rules
    annotation = SubElement(xml_model, "annotation")
    gpr_list = SubElement(annotation, "listOfGeneAssociations",
                          xmlns=ns["fbc"])
    for reaction in cobra_model.reactions:
        gpr = reaction.gene_reaction_rule
        r_id = reaction.id
        if gpr is not None and len(gpr) > 0:
            gpr = gpr.replace(" and ", " & ").replace(" or ", " | ")
            gpr = gpr.replace(".", "__COBRA_TMP_DOT__")
            gpr_xml = SubElement(gpr_list, "geneAssociation", id="ga_" + r_id,
                                 reaction="R_" + r_id)
            construct_gpr_xml(gpr_xml, sympy.sympify(gpr))

    return xml


def read_sbml_model(filename, number=float):
    xmlfile = parse(filename)
    xml = xmlfile.getroot()
    return parse_xml_into_model(xml, number=number)


def write_sbml_model(cobra_model, filename):
    xml = model_to_xml(cobra_model)
    if _with_lxml:
        xml_str = tostring(xml, pretty_print=True, encoding="UTF-8",
                           xml_declaration=True)
    else:
        minidom_xml = minidom.parseString(tostring(xml))
        xml_str = minidom_xml.toprettyxml(indent="  ", encoding="UTF-8")
    with open(filename, "w") as outfile:
        outfile.write(xml_str)
