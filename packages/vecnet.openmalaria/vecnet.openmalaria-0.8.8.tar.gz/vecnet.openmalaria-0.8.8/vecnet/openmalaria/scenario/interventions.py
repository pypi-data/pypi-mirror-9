#!/bin/env python2
# -*- coding: utf-8 -*-
#
# This file is part of the vecnet.openmalaria package.
# For copyright and licensing information about this package, see the
# NOTICE.txt and LICENSE.txt files in its top-level directory; they are
# available at https://github.com/vecnet/vecnet.openmalaria
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0.  If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.
from xml.etree.ElementTree import Element
from xml.etree import ElementTree

from vecnet.openmalaria.scenario.core import Section, attribute, attribute_setter, section, tag_value
from vecnet.openmalaria.scenario.healthsystem import HealthSystem


class Deployment(Section):
    @property
    @attribute
    def name(self):
        return "name", str

    @property
    @tag_value
    def id(self):
        return "component", "id", str

    @property
    def timesteps(self):
        deployments = []
        for deploy in self.et.find("timed").findall("deploy"):
            deployments.append(
                {"time":    int(deploy.attrib["time"]),
                 "coverage": float(deploy.attrib["coverage"])}
            )
        return deployments

    @property
    def continuous(self):
        deployments = []
        for deploy in self.et.find("continuous").findall("deploy"):
            deployments.append(
                    {"targetAgeYrs": float(deploy.attrib["targetAgeYrs"]),
                     "begin": int(deploy.attrib["begin"]) if 'begin' in deploy else 0,
                     "end": int(deploy.attrib["end"] if 'end' in deploy else 2147483647)
                    }
            )
        return deployments


class Deployments(Section):
    """
    Deployments defined in /scenario/interventions/human section
    """
    def __iter__(self):
        if self.et is None:
            return
        if self.et.find("deployment") is None:
            return
        for deployment in self.et.findall("deployment"):
            yield Deployment(deployment)

    def __len__(self):
        i = 0
        for deployment in self:
            i += 1
        return i


class Interventions(Section):
    """
    Inverventions section in OpenMalaria xml input file
    https://github.com/vecnet/om_schema_docs/wiki/GeneratedSchema32Doc#preventative-interventions
    """
    @property  # changeHS
    def changeHS(self):
        """
        Change health system interventions
        https://github.com/vecnet/om_schema_docs/wiki/GeneratedSchema32Doc#change-health-system
        Returns: list of HealthSystems together with timestep when they are applied
        """
        health_systems = []
        change_hs = self.et.find("changeHS")
        if change_hs is None:
            return health_systems
        for health_system in change_hs.findall("timedDeployment"):
            health_systems.append([int(health_system.attrib("time")), HealthSystem(self.et)])
        return health_systems

    @property  # changeEIR
    def changeEIR(self):
        change_eir = self.et.find("changeEIR")
        if change_eir is None:
            return None
        eir_daily = []
        for value in change_eir.findall("EIRDaily"):
            eir_daily.append(float(value.text))
        return eir_daily

    @property  # human
    def human(self):
        return HumanInterventions(self.et.find("human"))

    @property  # vectorPop
    def vectorPop(self):
        """
        rtype: VectorPop
        """
        return VectorPop(self.et.find("vectorPop"))

    def __getattr__(self, item):
        raise KeyError


class Component(Section):
    @property  # name
    @attribute
    def name(self):
        """
        An informal name/description of the intervention

        :rtype: str
        https://github.com/vecnet/om_schema_docs/wiki/GeneratedSchema32Doc#name-of-component
        """
        return "name", str
    @name.setter
    @attribute_setter(attrib_type=str)
    def name(self, value):
        pass   # value of name attribute will be set by attribute_setter decorator


class AnophelesParams(Section):
    """
    Parameters of mosquitos affected by this ITN intervention

    https://github.com/vecnet/om_schema_docs/wiki/GeneratedSchema32Doc#anophelesparams
    """
    @property
    @attribute
    def mosquito(self):
        """
        Name of the affected anopheles-mosquito species.

        https://github.com/vecnet/om_schema_docs/wiki/GeneratedSchema32Doc#anophelesparams
        """
        return "mosquito", str
    @mosquito.setter
    @attribute_setter(attrib_type=str)
    def mosquito(self, value):
        pass

    @property
    @attribute
    def propActive(self):
        """
        Proportion of bites for which net acts

        The proportion of bites, when nets are in use, for which the net has any action whatsoever on the mosquito.
        At the moment this is constant across humans and deterministic: relative attractiveness and survival factors
        are base(1-usagepropActing) + intervention_factorusagepropActing.
        See also "usage" (proportion of time nets are used by humans).

        https://github.com/vecnet/om_schema_docs/wiki/GeneratedSchema32Doc#proportion-of-bites-for-which-net-acts
        """
        return "propActive", float
    @propActive.setter
    @attribute_setter(attrib_type=float)
    def propActive(self, value):
        pass

    @property
    @tag_value
    def deterrency(self):
        return "deterrency", "value", float

    @property
    @tag_value
    def preprandialKillingEffect(self):
        return "preprandialKillingEffect", "value", float

    @property
    @tag_value
    def postprandialKillingEffect(self):
        return "postprandialKillingEffect", "value", float


class ITN(Component):
    def __init__(self, et):
        super(self.__class__, self).__init__(et)
        self.itn = et.find("ITN")
        self.id = self.et.attrib["id"]

    @property  # usage
    def usage(self):
        """
        Proportion of time nets are used by humans

        At the moment this is constant across humans and deterministic: relative attractiveness and survival factors
        are base(1-usagepropActing) + intervention_factorusagepropActing.
        See also "propActing" (proportion of bits for which net acts).

        https://github.com/vecnet/om_schema_docs/wiki/GeneratedSchema32Doc#proportion-of-time-nets-are-used-by-humans
        :rtype: float
        """
        return float(self.itn.find("usage").attrib["value"])
    @usage.setter
    def usage(self, value):
        assert isinstance(value, float)
        self.itn.find("usage").attrib["value"] = value

    @property
    # Same approach as with scenario.entomology.vectors may work here too
    def anophelesParams(self):
        """
        :rtype: AnophelesParams
        """
        list_of_anopheles = []
        for anophelesParams in self.itn.findall("anophelesParams"):
            list_of_anopheles.append(AnophelesParams(anophelesParams))
        return list_of_anopheles
    @anophelesParams.setter
    def anophelesParams(self, anopheles_params):
        for a_param in self.itn.findall("anophelesParams"):
            self.itn.remove(a_param) 

        for a_param in anopheles_params:
            assert isinstance(a_param, (str, unicode))
            et = ElementTree.fromstring(a_param)
            anopheles = AnophelesParams(et)
            assert isinstance(anopheles.mosquito, (str, unicode))
            assert isinstance(anopheles.propActive, float)
            assert isinstance(anopheles.deterrency, float)
            assert isinstance(anopheles.preprandialKillingEffect, float)
            assert isinstance(anopheles.postprandialKillingEffect, float)
            self.itn.append(et)

    def get_attrition_in_years(self):
        """
        Function for the Basic UI
        """
        attrition_of_nets = self.itn.find("attritionOfNets")
        function = attrition_of_nets.attrib["function"]
        if function != "step":
            return None
        L = attrition_of_nets.attrib["L"]
        return L

    def set_attrition_in_years(self, years):
        attrition_of_nets = self.itn.find("attritionOfNets")
        attrition_of_nets.attrib["function"] = "step"
        attrition_of_nets.attrib["L"] = years


class Decay(Section):
    """
    Description of decay of all intervention effects. Documentation:
    see DecayFunction type or http://code.google.com/p/openmalaria/wiki/ModelDecayFunctions

    https://github.com/vecnet/om_schema_docs/wiki/GeneratedSchema32Doc#decay-n4
    """
    @property
    @attribute
    def function(self):
        return "function", str

    @property
    @attribute
    def L(self):
        return "L", float

    @property
    @attribute
    def k(self):
        return "k", float

    @property
    @attribute
    def mu(self):
        return "mu", float

    @property
    @attribute
    def sigma(self):
        return "sigma", float


class GVI(Component):
    def __init__(self, et):
        super(self.__class__, self).__init__(et)
        self.gvi = et.find("GVI")
        self.id = self.et.attrib["id"]

    @property
    def decay(self):
        """
        :rtype: Decay
        """
        return Decay(self.gvi.find("decay"))

    @property
    # Same approach as with scenario.entomology.vectors may work here too
    def anophelesParams(self):
        """
        :rtype: AnophelesParams
        """
        list_of_anopheles = []
        for anophelesParams in self.gvi.findall("anophelesParams"):
            list_of_anopheles.append(AnophelesParams(anophelesParams))
        return list_of_anopheles
    @anophelesParams.setter
    def anophelesParams(self, anopheles_params):
        for a_param in self.gvi.findall("anophelesParams"):
            self.gvi.remove(a_param) 

        for a_param in anopheles_params:
            assert isinstance(a_param, (str, unicode))
            et = ElementTree.fromstring(a_param)
            anopheles = AnophelesParams(et)
            assert isinstance(anopheles.mosquito, (str, unicode))
            assert isinstance(anopheles.propActive, float)
            assert isinstance(anopheles.deterrency, float)
            assert isinstance(anopheles.preprandialKillingEffect, float)
            assert isinstance(anopheles.postprandialKillingEffect, float)
            self.gvi.append(et)


class Vaccine(Component):
    def __init__(self, et):
        super(self.__class__, self).__init__(et)

        self.vaccine_type = "TBV"
        self.vaccine = et.find("TBV")
        if (et.find("PEV") is not None):
            self.vaccine_type = "PEV"
            self.vaccine = et.find("PEV")
        elif (et.find("BSV") is not None):
            self.vaccine_type = "BSV"
            self.vaccine = et.find("BSV")

        self.id = self.et.attrib["id"]

    @property
    def decay(self):
        """
        :rtype: Decay
        """
        return Decay(self.vaccine.find("decay"))

    @property
    def efficacyB(self):
        return float(self.vaccine.find("efficacyB").attrib["value"])

    @property
    def initialEfficacy(self):
        values = []
        for initial_efficacy in self.vaccine.findall("initialEfficacy"):
            values.append(float(initial_efficacy.attrib["value"]))
        return values


class HumanInterventions(Section):
    """
    List of human interventions
    """

    @property
    def components(self):
        human_interventions = {}
        if self.et is None:
            # No /scenario/interventions/human section
            return {}
        for component in self.et.findall("component"):
            if component.find("ITN") is not None:
                human_interventions[component.attrib["id"]] = ITN(component)
            if component.find("GVI") is not None:
                human_interventions[component.attrib["id"]] = GVI(component)
            if component.find("TBV") is not None or component.find("PEV") is not None or component.find("BSV") is not None:
                human_interventions[component.attrib["id"]] = Vaccine(component)
        return human_interventions

    @property  # deployment
    def deployments(self):
        return Deployments(self.et)

    def __getitem__(self, item):
        """
        :rtype: Intervention
        """
        return self.components[item]

    def __getattr__(self, item):
        """
        :rtype: Intervention
        """
        return self.components[item]

    def __len__(self):
        return len(self.components)

    def __iter__(self):
        """
        Iterator function. Allows using scenario.interventions.human in for statement
        i.e.
        for intervention in scenario.interventions.human:
           print intervention.name

        :rtype: Vector
        """
        if not self.components:
            return
        for intervention_name, intervention in self.components.iteritems():
            yield intervention


class Anopheles(Section):
    """
    Mosquitos affected by VectorPop intervention

    https://github.com/vecnet/om_schema_docs/wiki/GeneratedSchema32Doc#elt-anopheles
    """
    @property
    @attribute
    def mosquito(self):
        """
        Name of the affected anopheles-mosquito species.

        https://github.com/vecnet/om_schema_docs/wiki/GeneratedSchema32Doc#elt-anopheles
        """
        return "mosquito", str
    @mosquito.setter
    @attribute_setter(attrib_type=str)
    def mosquito(self, value):
        pass

    @property
    @tag_value
    def seekingDeathRateIncrease(self):
        return "seekingDeathRateIncrease", "initial", float

    @property
    @tag_value
    def probDeathOvipositing(self):
        return "probDeathOvipositing", "initial", float

    @property
    @tag_value
    def emergenceReduction(self):
        return "emergenceReduction", "initial", float

    @property
    def decay(self, name):
        section = self.et.find(name)

        if section is not None:
            return Decay(section.find("decay"))

        return section


class VectorPopIntervention(Section):
    """
    /scenario/intervention/vectorPop/intervention
    An intervention which may have various effects on the vector populations as a whole
    """
    @property
    @attribute
    def name(self):  # name
        """
        Name of intervention (e.g. larviciding, sugar bait)
        https://github.com/vecnet/om_schema_docs/wiki/GeneratedSchema32Doc#name-of-intervention-6
        rtype: str
        """
        return "name", str
    @name.setter
    @attribute_setter(attrib_type=str)
    def name(self, value):
        pass  # attribute_setter decorator will change name attribute

    @property
    def anopheles(self):
        """
        :rtype: Anopheles
        """
        list_of_anopheles = []
        desc = self.et.find("description")

        if desc is not None:
            for anopheles in desc.findall("anopheles"):
                list_of_anopheles.append(Anopheles(anopheles))

        return list_of_anopheles
    @anopheles.setter
    def anopheles(self, anopheles):
        desc = self.et.find("description")

        if desc is not None:
            for anoph in desc.findall("anopheles"):
                desc.remove(anoph) 

            for a in anopheles:
                assert isinstance(a, (str, unicode))
                et = ElementTree.fromstring(a)
                anopheles = Anopheles(et)
                assert isinstance(anopheles.mosquito, (str, unicode))
                if anopheles.seekingDeathRateIncrease is not None:
                    assert isinstance(anopheles.seekingDeathRateIncrease, float)
                if anopheles.probDeathOvipositing is not None:
                    assert isinstance(anopheles.probDeathOvipositing, float)
                if anopheles.emergenceReduction is not None:
                    assert isinstance(anopheles.emergenceReduction, float)
                desc.append(et)

    @property
    def timesteps(self):
        """
        Time-step at which this intervention occurs, starting from 0, the first intervention-period time-step.
        https://github.com/vecnet/om_schema_docs/wiki/GeneratedSchema32Doc#-deploy-1
        rtype: list
        """
        timesteps = []
        timed = self.et.find("timed")

        if timed is not None:
            for deploy in timed.findall("deploy"):
                timesteps.append(deploy.attrib["time"])

        return timesteps


class VectorPop(Section):
    """
    /scenario/interventions/vectorPop
    Vector population intervention
    A list of parameterisations of generic vector host-inspecific interventions.
    https://github.com/vecnet/om_schema_docs/wiki/GeneratedSchema32Doc#elt-vectorPop
    """
    @property
    def interventions(self):
        """ List of interventions in /scenario/interventions/vectorPop section """
        array = []
        if self.et is None:
            return array
        for intervention in self.et.findall("intervention"):
            array.append(VectorPopIntervention(intervention))
        return array

    def __len__(self):
        return len(self.interventions)

    def __iter__(self):
        """
        Interator function. Allows using scenario.interventions.vectorPop in for statements
        for example:
        for interventions in scenario.interventions.vectorPop:
            print intervention.name
        :rtype: VectorPopIntervention
        """
        if len(self.interventions) == 0:
            return
        for intervention in self.interventions:
            yield intervention

    def __getitem__(self, item):
        return self.interventions[item]
