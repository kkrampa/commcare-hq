from django.utils.translation import ugettext_noop as _

from custom.apps.crs_reports.reports import HBNCMotherReport


CUSTOM_REPORTS = (
    (_('Custom Reports'), (
       HBNCMotherReport,
    )),
)

QUESTION_TEMPLATES = (
    (HBNCMotherReport.slug, [
        { 'questions' :[
            {'case_property': 'section_a',
             'question': _('A. Ask Mother.')
            },
            {'case_property': 'meals',
            'question': _('Number of times mother takes full meals in 24 hours?'),
            },
            {'case_property': 'bleeding',
            'question': _('Bleeding. How many pads are changed in a day?'),
            },
            {'case_property': 'warm',
            'question': _('During the cold season is the baby being kept warm (near mother, clothed and wrapped properly)?'),
            },
            {'case_property': 'feeding',
            'question': _('Is the baby being fed properly (whenever hungry or at least 7-8 times in 24 hrs)?'),
            },
            {'case_property': 'incessant_cry',
            'question': _('Is baby crying incessantly or passing urine less than 6 times a day?'),
            },
            {'case_property': 'section_b',
            'question': _('B. Examination of mother'),
            },
            {'case_property': 'maternal_temp',
            'question': _('Temperature: Measure and Record?'),
            },
            {'case_property': 'discharge',
            'question': _('Foul smelling discharge and fever more than 100 degree F (37.8 degree C)?'),
            },
            {'case_property': 'maternal_fits',
            'question': _('Is mother speaking abnormally or having fits?'),
            },
            {'case_property': 'no_milk',
            'question': _('Mother has no milk since delivery or if perceives breast milk to be less?'),
            },
            {'case_property': 'sore_breast',
            'question': _('Cracked nipples/painful and/or engorged breast?'),
            }]
        },
        { 'questions' :[
            {'case_property': 'section_c',
             'question': _('C.  Examination of Baby')
            },
            {'case_property': 'baby_eye',
            'question': _('Are the eyes swollen or with pus?'),
            },
            {'case_property': 'weight',
            'question': _('Weight (on day 7,14,21,28)?'),
            },
            {'case_property': 'baby_temp',
            'question': _('Temperature: Measure and Record?'),
            },
            {'case_property': 'pustules',
            'question': _('Skin: Pus filled pustules?'),
            },
            {'case_property': 'cracks',
            'question': _('Cracks or redness on the skin fold (thigh/Axilla/Buttock)?'),
            },
            {'case_property': 'jaundice',
            'question': _('Yellowness in eyes of skin: Jaundice?'),
            }]
        },
        { 'questions' :[
            {'case_property': 'section_d',
             'question': _('D.  Sepsis Signs Checkup')
            },
            {'case_property': 'limbs',
            'question': _('All limbs up?'),
            },
            {'case_property': 'feeding_less',
            'question': _('Feeding Less/Stopped?'),
            },
            {'case_property': 'cry',
            'question': _('Cry Weak/Stopped?'),
            },
            {'case_property': 'abdomen_vomit',
            'question': _('Distant abdomen or mother says "baby vomits often"?'),
            },
            {'case_property': 'cold',
            'question': _('Mother says "baby is cold to touch" or baby\'s temperature?'),
            },
            {'case_property': 'chest',
            'question': _('>99 degree F (37.2 degree C) Chest in drawing?'),
            },
            {'case_property': 'pus',
            'question': _('Pus on umbilicus?'),
            }]
        }
    ]),
)