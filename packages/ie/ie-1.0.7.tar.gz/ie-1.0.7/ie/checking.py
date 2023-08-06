# -*- coding: utf-8 -*-
"""Module de validation the states number"""

import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))

import ie.states.ac as ac    
import ie.states.al as al
import ie.states.am as am
import ie.states.ap as ap
import ie.states.ba as ba
import ie.states.ce as ce
import ie.states.df as df
import ie.states.es as es
import ie.states.go as go
import ie.states.ma as ma
import ie.states.mt as mt
import ie.states.ms as ms
import ie.states.mg as mg
import ie.states.pa as pa
import ie.states.pb as pb
import ie.states.pe as pe
import ie.states.pr as pr
import ie.states.pi as pi
import ie.states.rj as rj
import ie.states.rn as rn
import ie.states.rs as rs
import ie.states.ro as ro
import ie.states.rr as rr
import ie.states.sc as sc
import ie.states.sp as sp
import ie.states.se as se
import ie.states.to as to

def start(state_registration_number, state_abbreviation):
    """
        This function is like a Facade to another modules that
        makes their own state validation.

        state_registration_number - string brazilian state registration number
        state_abbreviation  - state abbreviation

        AC (Acre)
        AL (Alagoas)
        AM (Amazonas)
        AP (Amapá)
        BA (Bahia)
        CE (Ceará)
        DF (Distrito Federal)
        ES (Espírito Santo')
        GO (Goias)
        MA (Maranhão)
        MG (Minas Gerais)
        MS (Mato Grosso do Sul)
        MT (Mato Grosso)
        PA (Pará)
        PB (Paraíba)
        PE (Pernambuco)
        PI (Piauí)
        PR (Paraná)
        RJ (Rio de Janeiro)
        RN (Rio Grande do Norte)
        RO (Rondônia)
        RR (Roraima)
        RS (Rio Grande do Sul)
        SC (Santa Catarina)
        SE (Sergipe)
        SP (São Paulo)
        TO (Tocantins)
    """

    state_abbreviation = state_abbreviation.upper()
    states_validations = {
        'AC': "ac.start(" + "\"" + state_registration_number + "\"" + ")",
        'AL': "al.start(" + "\"" + state_registration_number + "\"" + ")",
        'AM': "am.start(" + "\"" + state_registration_number + "\"" + ")",
        'AP': "ap.start(" + "\"" + state_registration_number + "\"" + ")",
        'BA': "ba.start(" + "\"" + state_registration_number + "\"" + ")",
        'CE': "ce.start(" + "\"" + state_registration_number + "\"" + ")",
        'DF': "df.start(" + "\"" + state_registration_number + "\"" + ")",
        'ES': "es.start(" + "\"" + state_registration_number + "\"" + ")",
        'GO': "go.start(" + "\"" + state_registration_number + "\"" + ")",
        'MA': "ma.start(" + "\"" + state_registration_number + "\"" + ")",
        'MG': "mg.start(" + "\"" + state_registration_number + "\"" + ")",
        'MS': "ms.start(" + "\"" + state_registration_number + "\"" + ")",
        'MT': "mt.start(" + "\"" + state_registration_number + "\"" + ")",
        'PA': "pa.start(" + "\"" + state_registration_number + "\"" + ")",
        'PB': "pb.start(" + "\"" + state_registration_number + "\"" + ")",
        'PE': "pe.start(" + "\"" + state_registration_number + "\"" + ")",
        'PI': "pi.start(" + "\"" + state_registration_number + "\"" + ")",
        'PR': "pr.start(" + "\"" + state_registration_number + "\"" + ")",
        'RJ': "rj.start(" + "\"" + state_registration_number + "\"" + ")",
        'RN': "rn.start(" + "\"" + state_registration_number + "\"" + ")",
        'RO': "ro.start(" + "\"" + state_registration_number + "\"" + ")",
        'RR': "rr.start(" + "\"" + state_registration_number + "\"" + ")",
        'RS': "rs.start(" + "\"" + state_registration_number + "\"" + ")",
        'SC': "sc.start(" + "\"" + state_registration_number + "\"" + ")",
        'SE': "se.start(" + "\"" + state_registration_number + "\"" + ")",
        'SP': "sp.start(" + "\"" + state_registration_number + "\"" + ")",
        'TO': "to.start(" + "\"" + state_registration_number + "\"" + ")"

    }

    exec('validity = ' + states_validations[state_abbreviation])
    return validity
