position_model = '''
    class DemoPosition(auto_prefetch.Model):
    OPEN = 'open'
    CLOSED = 'close'
    PENDING = 'pending'
    CANCELLED = 'cancelled'
    
    STATE_CHOICES = [
        (OPEN, 'Open'),
        (CLOSED, 'Closed'),
        (PENDING,'Pending'),
        (CANCELLED, 'Cancel')
    ]
    stock = auto_prefetch.ForeignKey(Stock, on_delete=models.CASCADE, related_name='demopositions2')
    quantity = models.PositiveIntegerField(default=0)
    limit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    action = models.CharField(max_length=20, default='buy')
    '''
alert_model = '''
    class Alert(auto_prefetch.Model):
        stock= auto_prefetch.ForeignKey(Stock,on_delete=models.CASCADE)
        alert_type=models.CharField(max_length=30, choices=(("price", "price"), ("volume", "volume")), default='price')
        action=models.CharField(max_length=50, choices=(("above", "above"), ("below", "below")))
        to_price=models.FloatField(blank=True, null=True)
        to_volume=models.FloatField(blank=True, null=True)    
        frequency=models.CharField(max_length=50, choices=(("Once","Once"),("Everytime", "Everytime")))
        
    '''
pairs = {
  "ABBEY MORTGAGE BANK PLC [BLS]": "ABBEYBDS",
  "ACADEMY PRESS PLC.": "ACADEMY",
  "ACCESS HOLDINGS PLC [CG+]": "ACCESSCORP",
  "AFRICA PRUDENTIAL PLC [CG+]": "AFRIPRUD",
  "AFRICAN ALLIANCE INSURANCE PLC [MRF]": "AFRINSURE",
  "AFROMEDIA PLC [MRF]": "AFROMEDIA",
  "AIICO INSURANCE PLC.": "AIICO",
  "AIRTEL AFRICA PLC": "AIRTELAFRI",
  "ALUMINIUM EXTRUSION IND. PLC. [BLS]": "ALEX",
  "ARBICO PLC.": "ARBICO",
  "ASO SAVINGS AND LOANS PLC [DIP]": "ASOSAVINGS",
  "ASSOCIATED BUS COMPANY PLC": "ABCTRANS",
  "AUSTIN LAZ & COMPANY PLC": "AUSTINLAZ",
  "AXAMANSARD INSURANCE PLC [CG+]": "MANSARD",
  "BERGER PAINTS PLC [CG+]": "BERGER",
  "BETA GLASS PLC.": "BETAGLAS",
  "BRICLINKS AFRICA PLC": "BAPLC",
  "BUA CEMENT PLC": "BUACEMENT",
  "BUA FOODS PLC": "BUAFOODS",
  "C & I LEASING PLC.": "CILEASING",
  "CADBURY NIGERIA PLC.": "CADBURY",
  "CAP PLC": "CAP",
  "CAPITAL OIL PLC [MRF]": "CAPOIL",
  "CAVERTON OFFSHORE SUPPORT GRP PLC": "CAVERTON",
  "CHAMPION BREW. PLC. [BLS]": "CHAMPION",
  "CHAMS HOLDING COMPANY PLC": "CHAMS",
  "CHAPEL HILL DENHAM NIG. INFRAS DEBT FUND": "NIDF",
  "CHELLARAMS PLC.": "CHELLARAM",
  "CONOIL PLC": "CONOIL",
  "CONSOLIDATED HALLMARK INSURANCE PLC": "CHIPLC",
  "CORNERSTONE INSURANCE PLC [CG+]": "CORNERST",
  "CORONATION INSURANCE PLC [CG+]": "WAPIC",
  "CUSTODIAN INVESTMENT PLC [CG+]": "CUSTODIAN",
  "CUTIX PLC.": "CUTIX",
  "CWG PLC [BLS]": "CWG",
  "DAAR COMMUNICATIONS PLC": "DAARCOMM",
  "DANGOTE CEMENT PLC [CG+]": "DANGCEM",
  "DANGOTE SUGAR REFINERY PLC [CG+]": "DANGSUGAR",
  "DEAP CAPITAL MANAGEMENT & TRUST PLC [DWL]": "DEAPCAP",
  "DN TYRE & RUBBER PLC [MRS]": "DUNLOP",
  "E-TRANZACT INTERNATIONAL PLC [BLS][CG+]": "ETRANZACT",
  "ECOBANK TRANSNATIONAL INCORPORATED [MRF]": "ETI",
  "EKOCORP PLC. [BMF]": "EKOCORP",
  "ELLAH LAKES PLC.": "ELLAHLAKES",
  "ETERNA PLC.": "ETERNA",
  "EUNISELL INTERLINKED PLC": "EUNISELL",
  "FBN HOLDINGS PLC [CG+]": "FBNH",
  "FCMB GROUP PLC. [MRF]": "FCMB",
  "FIDELITY BANK PLC [CG+]": "FIDELITYBK",
  "FIDSON HEALTHCARE PLC": "FIDSON",
  "FLOUR MILLS NIG. PLC. [CG+]": "FLOURMILL",
  "FTN COCOA PROCESSORS PLC [RST]": "FTNCOCOA",
  "GEREGU POWER PLC": "GEREGU",
  "GLAXO SMITHKLINE CONSUMER NIG. PLC. [CG+]": "GLAXOSMITH",
  "GOLDEN GUINEA BREW. PLC. [BMF]": "GOLDBREW",
  "GOLDLINK INSURANCE PLC [MRS]": "GOLDINSURE",
  "GREIF NIGERIA PLC": "VANLEER",
  "GUARANTY TRUST HOLDING COMPANY PLC [CG+]": "GTCO",
  "GUINEA INSURANCE PLC.": "GUINEAINS",
  "GUINNESS NIG PLC [CG+]": "GUINNESS",
  "HONEYWELL FLOUR MILL PLC [BLS][CG+]": "HONYFLOUR",
  "IKEJA HOTEL PLC": "IKEJAHOTEL",
  "INDUSTRIAL & MEDICAL GASES NIGERIA PLC": "IMG",
  "INFINITY TRUST MORTGAGE BANK PLC [BLS]": "INFINITY",
  "INTERNATIONAL BREWERIES PLC. [BLS]": "INTBREW",
  "INTERNATIONAL ENERGY INSURANCE PLC [MRS]": "INTENEGINS",
  "JAIZ BANK PLC": "JAIZBANK",
  "JAPAUL GOLD & VENTURES PLC": "JAPAULGOLD",
  "JOHN HOLT PLC.": "JOHNHOLT",
  "JULI PLC.": "JULI",
  "JULIUS BERGER NIG. PLC. [CG+]": "JBERGER",
  "LAFARGE AFRICA PLC. [CG+]": "WAPCO",
  "LASACO ASSURANCE PLC.": "LASACO",
  "LEARN AFRICA PLC": "LEARNAFRCA",
  "LINKAGE ASSURANCE PLC": "LINKASSURE",
  "LIVESTOCK FEEDS PLC.": "LIVESTOCK",
  "LIVINGTRUST MORTGAGE BANK PLC": "LIVINGTRUST",
  "MAY & BAKER NIGERIA PLC.": "MAYBAKER",
  "MCNICHOLS PLC": "MCNICHOLS",
  "MEDVIEW AIRLINE PLC [BMF]": "MEDVIEWAIR",
  "MEYER PLC.": "MEYER",
  "MORISON INDUSTRIES PLC.": "MORISON",
  "MRS OIL NIGERIA PLC.": "MRS",
  "MTN NIGERIA COMMUNICATIONS PLC [CG+]": "MTNN",
  "MULTI-TREX INTEGRATED FOODS PLC [DWL]": "MULTITREX",
  "MULTIVERSE MINING AND EXPLORATION PLC": "MULTIVERSE",
  "MUTUAL BENEFITS ASSURANCE PLC.": "MBENEFIT",
  "N NIG. FLOUR MILLS PLC.": "NNFM",
  "NASCON ALLIED INDUSTRIES PLC": "NASCON",
  "NCR (NIGERIA) PLC.": "NCR",
  "NEIMETH INTERNATIONAL PHARMACEUTICALS PLC [CG+]": "NEIMETH",
  "NEM INSURANCE PLC [CG+]": "NEM",
  "NESTLE NIGERIA PLC. [CG+]": "NESTLE",
  "NIGER INSURANCE PLC [MRF]": "NIGERINS",
  "NIGERIA ENERYGY SECTOR FUND": "NESF",
  "NIGERIAN AVIATION HANDLING COMPANY PLC [CG+]": "NAHCO",
  "NIGERIAN BREW. PLC. [CG+]": "NB",
  "NIGERIAN ENAMELWARE PLC.": "ENAMELWA",
  "NIGERIAN EXCHANGE GROUP": "NGXGROUP",
  "NOTORE CHEMICAL IND PLC [BLS]": "NOTORE",
  "NPF MICROFINANCE BANK PLC [CG+]": "NPFMCRFBK",
  "OANDO PLC [MRF]": "OANDO",
  "OKOMU OIL PALM PLC.": "OKOMUOIL",
  "OMATEK VENTURES PLC [RST]": "OMATEK",
  "P Z CUSSONS NIGERIA PLC. [CG+]": "PZ",
  "PHARMA-DEKO PLC. [MRF]": "PHARMDEKO",
  "PREMIER PAINTS PLC. [MRF]": "PREMPAINTS",
  "PRESCO PLC": "PRESCO",
  "PRESTIGE ASSURANCE PLC [BLS]": "PRESTIGE",
  "R T BRISCOE PLC.": "RTBRISCOE",
  "RAK UNITY PET. COMP. PLC. [MRF]": "RAKUNITY",
  "RED STAR EXPRESS PLC [CG+]": "REDSTAREX",
  "REGENCY ASSURANCE PLC": "REGALINS",
  "RESORT SAVINGS & LOANS PLC [MRF]": "RESORTSAL",
  "RONCHESS GLOBAL RESOURCES PLC": "RONCHESS",
  "ROYAL EXCHANGE PLC. [CG+]": "ROYALEX",
  "S C O A NIG. PLC.": "SCOA",
  "SECURE ELECTRONIC TECHNOLOGY PLC": "NSLTECH",
  "SEPLAT ENERGY PLC [CG+]": "SEPLAT",
  "SFS REAL ESTATE INVESTMENT TRUST": "SFSREIT",
  "SKYWAY AVIATION HANDLING COMPANY PLC": "SKYAVN",
  "SMART PRODUCTS NIGERIA PLC [MRF]": "SMURFIT",
  "SOVEREIGN TRUST INSURANCE PLC": "SOVRENINS",
  "STACO INSURANCE PLC [MRF]": "STACO",
  "STANBIC IBTC HOLDINGS PLC [CG+]": "STANBIC",
  "STANDARD ALLIANCE INSURANCE PLC. [MRF]": "STDINSURE",
  "STERLING FINANCIAL HOLDINGS COMPANY PLC": "STERLINGNG",
  "SUNU ASSURANCES NIGERIA PLC. [CG+]": "SUNUASSUR",
  "TANTALIZERS PLC": "TANTALIZER",
  "THE INITIATES PLC": "TIP",
  "THOMAS WYATT NIG. PLC. [RTS]": "THOMASWY",
  "TOTALENERGIES MARKETING NIGERIA PLC": "TOTAL",
  "TOURIST COMPANY OF NIGERIA PLC. [DIP]": "TOURIST",
  "TRANS-NATIONWIDE EXPRESS PLC.": "TRANSEXPR",
  "TRANSCORP HOTELS PLC [CG+]": "TRANSCOHOT",
  "TRANSNATIONAL CORPORATION PLC": "TRANSCORP",
  "TRIPPLE GEE AND COMPANY PLC.": "TRIPPLEG",
  "U A C N PLC.": "UACN",
  "UH REAL ESTATE INVESTMENT TRUST": "UHOMREIT",
  "UNILEVER NIGERIA PLC. [CG+]": "UNILEVER",
  "UNION BANK NIG.PLC. [BMF]": "UBN",
  "UNION DICON SALT PLC. [BRS]": "UNIONDICON",
  "UNION HOMES SAVINGS AND LOANS PLC. [DIP]": "UNHOMES",
  "UNITED BANK FOR AFRICA PLC [CG+]": "UBA",
  "UNITED CAPITAL PLC [CG+]": "UCAP",
  "UNITY BANK PLC": "UNITYBNK",
  "UNIVERSAL INSURANCE PLC": "UNIVINSURE",
  "UNIVERSITY PRESS PLC.": "UPL",
  "UPDC PLC [BLS]": "UPDC",
  "UPDC REAL ESTATE INVESTMENT TRUST": "UPDCREIT",
  "VERITAS KAPITAL ASSURANCE PLC": "VERITASKAP",
  "VFD GROUP PLC": "VFDGROUP",
  "VITAFOAM NIG PLC.": "VITAFOAM",
  "WEMA BANK PLC. [CG+]": "WEMABANK",
  "ZENITH BANK PLC [CG+]": "ZENITHBANK"
}

supported_indicators = ['current price', 'exponential moving average of price', 'moving average of price', 'relative strength index', 'standard deviation of price']