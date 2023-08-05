"""
This file reads input csv file and saves the variables 
"""

import pandas as pd
import numpy as np
import os.path


class Records(object):
    """
    This class represents the data for a collection of tax records. Typically,
    this would come from a Public Use File. Much of the current implementation
    is based on reading a PUF file, although other types of records could
    be read.
    Instances of this class hold all of the record data in memory
    to be used by the Calculator. Each pieces of member data represents
    a column of the data. Each entry in the column is the value of the data
    attribute for a particular taxpayer record.
    A federal tax year is assumed. The year can be given to the Record
    constructor.
    Advancing years is done through a member function
    """

    @classmethod
    def from_file(cls, path, **kwargs):
        return cls(path, **kwargs)

    def __init__(self, data="puf2.csv", start_year=None):

        self.read(data)
        if (start_year):
            self._current_year = start_year
        else:
            self._current_year = self.FLPDYR[0]

    @property
    def current_year(self):
        return self._current_year

    def increment_year(self):
        self._current_year += 1
        self.FLPDYR += 1

    def read(self, data):
        if isinstance(data, pd.core.frame.DataFrame):
            tax_dta = data
        elif data.endswith("gz"):
            tax_dta = pd.read_csv(data, compression='gzip')
        else:
            tax_dta = pd.read_csv(data)

        # pairs of 'name of attribute', 'column name' - often the same
        names = [('AGIR1', 'agir1'),
                 ('DSI', 'dsi'),
                 ('EFI', 'efi'),
                 ('EIC', 'eic'),
                 ('ELECT', 'elect'),
                 ('FDED', 'fded'),
                 ('FLPDYR', 'flpdyr'),
                 ('FLPDMO', 'flpdmo'),
                 ('f2441', 'f2441'),
                 ('f3800', 'f3800'),
                 ('f6251', 'f6251'),
                 ('f8582', 'f8582'),
                 ('f8606', 'f8606'),
                 ('IE', 'ie'),
                 ('MARS', 'mars'),
                 ('MIdR', 'midr'),
                 ('n20', 'n20'),
                 ('n24', 'n24'),
                 ('n25', 'n25'),
                 ('PREP', 'prep'),
                 ('SCHB', 'schb'),
                 ('SCHCF', 'schcf'),
                 ('SCHE', 'sche'),
                 ('STATE', 'state'),
                 ('TFORM', 'tform'),
                 ('TXST', 'txst'),
                 ('XFPT', 'xfpt'),
                 ('XFST', 'xfst'),
                 ('XOCAH', 'xocah'),
                 ('XOCAWH', 'xocawh'),
                 ('XOODEP', 'xoodep'),
                 ('XOPAR', 'xopar'),
                 ('XTOT', 'xtot'),
                 ('e00200', 'e00200'),
                 ('e00300', 'e00300'),
                 ('e00400', 'e00400'),
                 ('e00600', 'e00600'),
                 ('e00650', 'e00650'),
                 ('e00700', 'e00700'),
                 ('e00800', 'e00800'),
                 ('e00900', 'e00900'),
                 ('e01000', 'e01000'),
                 ('e01100', 'e01100'),
                 ('e01200', 'e01200'),
                 ('e01400', 'e01400'),
                 ('e01500', 'e01500'),
                 ('e01700', 'e01700'),
                 ('e02000', 'e02000'),
                 ('e02100', 'e02100'),
                 ('e02300', 'e02300'),
                 ('e02400', 'e02400'),
                 ('e02500', 'e02500'),
                 ('e03150', 'e03150'),
                 ('e03210', 'e03210'),
                 ('e03220', 'e03220'),
                 ('e03230', 'e03230'),
                 ('e03260', 'e03260'),
                 ('e03270', 'e03270'),
                 ('e03240', 'e03240'),
                 ('e03290', 'e03290'),
                 ('e03300', 'e03300'),
                 ('e03400', 'e03400'),
                 ('e03500', 'e03500'),
                 ('e00100', 'e00100'),
                 ('p04470', 'p04470'),
                 ('e04250', 'e04250'),
                 ('e04600', 'e04600'),
                 ('e04800', 'e04800'),
                 ('e05100', 'e05100'),
                 ('e05200', 'e05200'),
                 ('e05800', 'e05800'),
                 ('e06000', 'e06000'),
                 ('e06200', 'e06200'),
                 ('e06300', 'e06300'),
                 ('e09600', 'e09600'),
                 ('e07180', 'e07180'),
                 ('e07200', 'e07200'),
                 ('e07220', 'e07220'),
                 ('e07230', 'e07230'),
                 ('e07240', 'e07240'),
                 ('e07260', 'e07260'),
                 ('e07300', 'e07300'),
                 ('e07400', 'e07400'),
                 ('e07600', 'e07600'),
                 ('p08000', 'p08000'),
                 ('e07150', 'e07150'),
                 ('e06500', 'e06500'),
                 ('e08800', 'e08800'),
                 ('e09400', 'e09400'),
                 ('e09700', 'e09700'),
                 ('e09800', 'e09800'),
                 ('e09900', 'e09900'),
                 ('e10300', 'e10300'),
                 ('e10700', 'e10700'),
                 ('e10900', 'e10900'),
                 ('e59560', 'e59560'),
                 ('e59680', 'e59680'),
                 ('e59700', 'e59700'),
                 ('e59720', 'e59720'),
                 ('e11550', 'e11550'),
                 ('e11070', 'e11070'),
                 ('e11100', 'e11100'),
                 ('e11200', 'e11200'),
                 ('e11300', 'e11300'),
                 ('e11400', 'e11400'),
                 ('e11570', 'e11570'),
                 ('e11580', 'e11580'),
                 ('e11581', 'e11581'),
                 ('e11582', 'e11582'),
                 ('e11583', 'e11583'),
                 ('e10605', 'e10605'),
                 ('e11900', 'e11900'),
                 ('e12000', 'e12000'),
                 ('e12200', 'e12200'),
                 ('e17500', 'e17500'),
                 ('e18425', 'e18425'),
                 ('e18450', 'e18450'),
                 ('e18500', 'e18500'),
                 ('e19200', 'e19200'),
                 ('e19550', 'e19550'),
                 ('e19800', 'e19800'),
                 ('e20100', 'e20100'),
                 ('e19700', 'e19700'),
                 ('e20550', 'e20550'),
                 ('e20600', 'e20600'),
                 ('e20400', 'e20400'),
                 ('e20800', 'e20800'),
                 ('e20500', 'e20500'),
                 ('e21040', 'e21040'),
                 ('p22250', 'p22250'),
                 ('e22320', 'e22320'),
                 ('e22370', 'e22370'),
                 ('p23250', 'p23250'),
                 ('e24515', 'e24515'),
                 ('e24516', 'e24516'),
                 ('e24518', 'e24518'),
                 ('e24535', 'e24535'),
                 ('e24560', 'e24560'),
                 ('e24598', 'e24598'),
                 ('e24615', 'e24615'),
                 ('e24570', 'e24570'),
                 ('p25350', 'p25350'),
                 ('e25370', 'e25370'),
                 ('e25380', 'e25380'),
                 ('p25470', 'p25470'),
                 ('p25700', 'p25700'),
                 ('e25820', 'e25820'),
                 ('e25850', 'e25850'),
                 ('e25860', 'e25860'),
                 ('e25940', 'e25940'),
                 ('e25980', 'e25980'),
                 ('e25920', 'e25920'),
                 ('e25960', 'e25960'),
                 ('e26110', 'e26110'),
                 ('e26170', 'e26170'),
                 ('e26190', 'e26190'),
                 ('e26160', 'e26160'),
                 ('e26180', 'e26180'),
                 ('e26270', 'e26270'),
                 ('e26100', 'e26100'),
                 ('e26390', 'e26390'),
                 ('e26400', 'e26400'),
                 ('e27200', 'e27200'),
                 ('e30400', 'e30400'),
                 ('e30500', 'e30500'),
                 ('e32800', 'e32800'),
                 ('e33000', 'e33000'),
                 ('e53240', 'e53240'),
                 ('e53280', 'e53280'),
                 ('e53410', 'e53410'),
                 ('e53300', 'e53300'),
                 ('e53317', 'e53317'),
                 ('e53458', 'e53458'),
                 ('e58950', 'e58950'),
                 ('e58990', 'e58990'),
                 ('p60100', 'p60100'),
                 ('p61850', 'p61850'),
                 ('e60000', 'e60000'),
                 ('e62100', 'e62100'),
                 ('e62900', 'e62900'),
                 ('e62720', 'e62720'),
                 ('e62730', 'e62730'),
                 ('e62740', 'e62740'),
                 ('p65300', 'p65300'),
                 ('p65400', 'p65400'),
                 ('e68000', 'e68000'),
                 ('e82200', 'e82200'),
                 ('t27800', 't27800'),
                 ('e27860', 's27860'),
                 ('p27895', 'p27895'),
                 ('e87500', 'e87500'),
                 ('e87510', 'e87510'),
                 ('e87520', 'e87520'),
                 ('e87530', 'e87530'),
                 ('e87540', 'e87540'),
                 ('e87550', 'e87550'),
                 ('RECID', 'recid'),
                 ('s006', 's006'),
                 ('s008', 's008'),
                 ('s009', 's009'),
                 ('WSAMP', 'wsamp'),
                 ('TXRT', 'txrt'),
                ]

        self.dim = len(tax_dta)

        for attrname, varname in names:
            setattr(self, attrname, tax_dta[varname].values)

        # zero'd out "nonconst" data
        zeroed_names = ['e35300_0', 'e35600_0', 'e35910_0', 'x03150', 'e03600',
                        'e03280', 'e03900', 'e04000', 'e03700', 'c23250',
                        'e23660', 'f2555', 'e02800', 'e02610', 'e02540',
                        'e02615', 'SSIND', 'e18400', 'e18800', 'e18900',
                        'e20950', 'e19500', 'e19570', 'e19400', 'c20400',
                        'e20200', 'e20900', 'e21000', 'e21010', 'e02600',
                        '_exact', 'e11055', 'e00250', 'e30100', 'e15360',
                        'e04200', 'e37717', 'e04805', 'AGEP', 'AGES', 'PBI',
                        'SBI', 't04470', 'e58980', 'c00650', 'c00100',
                        'c04470', 'c04600', 'c21060', 'c21040', 'c17000',
                        'c18300', 'c20800', 'c02900', 'c02700', 'c23650',
                        'c01000', 'c02500', 'e24583', '_fixup', '_cmp',
                        'e59440', 'e59470', 'e59400', 'e10105', 'e83200_0',
                        'e59410', 'e59420', 'e74400', 'x62720', 'x60260',
                        'x60240', 'x60220', 'x60130', 'x62730', 'e60290',
                        'DOBYR', 'SDOBYR', 'DOBMD', 'SDOBMD', 'e62600',
                        'x62740', '_fixeic', 'e32880', 'e32890', 'CDOB1',
                        'CDOB2', 'e32750', 'e32775', 'e33420', 'e33430',
                        'e33450', 'e33460', 'e33465', 'e33470', 'x59560',
                        'EICYB1', 'EICYB2', 'EICYB3', 'e83080', 'e25360',
                        'e25430', 'e25400', 'e25500', 'e26210', 'e26340',
                        'e26205', 'e26320', 'e87482', 'e87487', 'e87492',
                        'e87497', 'e87526', 'e87522', 'e87524', 'e87528',
                        'EDCRAGE', 'e07960', 'e07700', 'e07250', 't07950',
                        'e82882', 'e82880', 'e07500', 'e08001', 'e07970',
                        'e07980', 'e10000', 'e10100', 'e10050', 'e10075',
                        'e09805', 'e09710', 'e09720', 'e87900', 'e87905',
                        'e87681', 'e87682', 'e11451', 'e11452', 'e11601',
                        'e11602', 'e60300', 'e60860', 'e60840', 'e60630',
                        'e60550', 'e60720', 'e60430', 'e60500', 'e60340',
                        'e60680', 'e60600', 'e60405', 'e60440', 'e60420',
                        'e60410', 'e61400', 'e60660', 'e60480', 'e62000',
                        'e60250', 'e40223', '_sep', '_earned', '_sey',
                        '_setax', '_feided', '_ymod', '_ymod1', '_posagi',
                        '_sit', 'xtxcr1xtxcr10', '_earned', '_xyztax',
                        '_taxinc', 'c04800', '_feitax', 'c05750', 'c24517',
                        '_taxbc', 'c60000', '_standard', 'c24516', 'c25420',
                        'c05700', 'c32880', 'c32890', '_dclim', 'c32800',
                        'c33000', 'c05800', '_othtax', 'c59560', '_agep',
                        '_ages', 'c87521', 'c87550', 'c07180',
                        'c07230', '_precrd', 'c07220', 'c59660', 'c07970',
                        'c08795', 'c09200', 'c07100', '_eitc', 'c59700',
                        'c10950', '_ymod2', '_ymod3', 'c02650', '_agierr',
                        '_ywossbe', '_ywossbc', '_prexmp', 'c17750', '_sit1',
                        '_statax', 'c37703', 'c20500', 'c20750', 'c19200',
                        'c19700', '_nonlimited', '_limitratio', '_phase2_i',
                        '_fica', '_seyoff', 'c11055', 'c15100', '_numextra',
                        '_txpyers', 'c15200', '_othded', 'c04100', 'c04200',
                        'c04500', '_amtstd', '_oldfei', 'c05200', '_cglong',
                        '_noncg', '_hasgain', '_dwks9', '_dwks5', '_dwks12',
                        '_dwks16', '_dwks17', '_dwks21', '_dwks25', '_dwks26',
                        '_dwks28', '_dwks31', 'c24505', 'c24510', 'c24520',
                        'c24530', 'c24540', 'c24534', 'c24597', 'c24598',
                        'c24610', 'c24615', 'c24550', 'c24570', '_addtax',
                        'c24560', '_taxspecial', 'c24580', 'c05100', 'c05700',
                        'c59430', 'c59450', 'c59460', '_line17', '_line19',
                        '_line22', '_line30', '_line31', '_line32', '_line36',
                        '_line33', '_line34', '_line35', 'c59485', 'c59490',
                        '_s1291', '_parents', 'c62720', 'c60260', 'c63100',
                        'c60200', 'c60240', 'c60220', 'c60130', 'c62730',
                        '_addamt', 'c62100', '_cmbtp', '_edical', '_amtsepadd',
                        '_agep', '_ages', 'c62600', 'c62700', '_alminc',
                        '_amtfei','c62780', 'c62900', 'c63000', 'c62740',
                        '_ngamty', 'c62745', 'y62745', '_tamt2', '_amt5pc',
                        '_amt15pc', '_amt25pc', 'c62747', 'c62755', 'c62770',
                        '_amt', 'c62800', 'c09600', 'c05800', '_ncu13',
                        '_seywage', 'c33465', 'c33470', 'c33475', 'c33480',
                        'c32840', '_tratio', 'c33200', 'c33400', 'c07180',
                        '_ieic', 'EICYB1', 'EICYB2', 'EICYB3', '_modagi',
                        '_val_ymax', '_preeitc', '_val_rtbase', '_val_rtless',
                        '_dy', 'c11070', '_nctcr', '_ctcagi', 'c87482',
                        'c87487', 'c87492', 'c87497', 'c87483', 'c87488',
                        'c87493', 'c87498', 'c87540', 'c87530', 'c87654',
                        'c87656', 'c87658', 'c87660', 'c87662', 'c87664',
                        'c87666', 'c10960', 'c87668', 'c87681', 'c87560',
                        'c87570', 'c87580', 'c87590', 'c87600', 'c87610',
                        'c87620', '_ctc1', '_ctc2', '_regcrd', '_exocrd',
                        '_ctctax', 'c07220', 'c82925', 'c82930', 'c82935',
                        'c82880', 'h82880', 'c82885', 'c82890', 'c82900',
                        'c82905', 'c82910', 'c82915',  'c82920', 'c82937',
                        'c82940', 'c11070', 'e59660', '_othadd', 'y07100',
                        'x07100', 'c08800', 'e08795', 'x07400', 'c59680',
                        'c59720', '_comb', 'c07150', 'c10300']
                        
                        

        for name in zeroed_names:
            setattr(self, name, np.zeros((self.dim,)))

        self._num = np.ones((self.dim,))

        # Aliases
        self.e22250 = self.p22250
        self.e04470 = self.p04470
        self.e23250 = self.p23250
        self.e25470 = self.p25470
        self.e08000 = self.p08000
        self.e60100 = self.p60100
        self.SOIYR = np.repeat(2008, self.dim)
