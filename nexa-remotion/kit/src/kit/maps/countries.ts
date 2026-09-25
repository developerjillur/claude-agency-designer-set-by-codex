// Country lookup: every country and territory in world-atlas (Natural Earth admin 0) with its ISO 3166 numeric id,
// alpha-3 and alpha-2 codes and a display name, plus common aliases and Bangla names for the countries a
// Bangladeshi audience meets most. A `CountryRef` may be any of them: 'Bangladesh', 'BGD', 'BD', '050', 50,
// 'বাংলাদেশ'. world-atlas holds countries only: no states, divisions or cities (pass city coordinates yourself).

export type CountryRef = string | number;

type Row = [id: string, a3: string, a2: string, name: string, atlasName?: string];

// id: ISO numeric as world-atlas stores it ('n:' + atlas name for the five shapes that have no id).
const ROWS: Row[] = [
	['004', 'AFG', 'AF', 'Afghanistan'],
	['008', 'ALB', 'AL', 'Albania'],
	['010', 'ATA', 'AQ', 'Antarctica'],
	['012', 'DZA', 'DZ', 'Algeria'],
	['016', 'ASM', 'AS', 'American Samoa'],
	['020', 'AND', 'AD', 'Andorra'],
	['024', 'AGO', 'AO', 'Angola'],
	['028', 'ATG', 'AG', 'Antigua and Barbuda', 'Antigua and Barb.'],
	['031', 'AZE', 'AZ', 'Azerbaijan'],
	['032', 'ARG', 'AR', 'Argentina'],
	['036', 'AUS', 'AU', 'Australia'],
	['040', 'AUT', 'AT', 'Austria'],
	['044', 'BHS', 'BS', 'Bahamas'],
	['048', 'BHR', 'BH', 'Bahrain'],
	['050', 'BGD', 'BD', 'Bangladesh'],
	['051', 'ARM', 'AM', 'Armenia'],
	['052', 'BRB', 'BB', 'Barbados'],
	['056', 'BEL', 'BE', 'Belgium'],
	['060', 'BMU', 'BM', 'Bermuda'],
	['064', 'BTN', 'BT', 'Bhutan'],
	['068', 'BOL', 'BO', 'Bolivia'],
	['070', 'BIH', 'BA', 'Bosnia and Herzegovina', 'Bosnia and Herz.'],
	['072', 'BWA', 'BW', 'Botswana'],
	['076', 'BRA', 'BR', 'Brazil'],
	['084', 'BLZ', 'BZ', 'Belize'],
	['086', 'IOT', 'IO', 'British Indian Ocean Territory', 'Br. Indian Ocean Ter.'],
	['090', 'SLB', 'SB', 'Solomon Islands', 'Solomon Is.'],
	['092', 'VGB', 'VG', 'British Virgin Islands', 'British Virgin Is.'],
	['096', 'BRN', 'BN', 'Brunei'],
	['100', 'BGR', 'BG', 'Bulgaria'],
	['104', 'MMR', 'MM', 'Myanmar'],
	['108', 'BDI', 'BI', 'Burundi'],
	['112', 'BLR', 'BY', 'Belarus'],
	['116', 'KHM', 'KH', 'Cambodia'],
	['120', 'CMR', 'CM', 'Cameroon'],
	['124', 'CAN', 'CA', 'Canada'],
	['132', 'CPV', 'CV', 'Cabo Verde'],
	['136', 'CYM', 'KY', 'Cayman Islands', 'Cayman Is.'],
	['140', 'CAF', 'CF', 'Central African Republic', 'Central African Rep.'],
	['144', 'LKA', 'LK', 'Sri Lanka'],
	['148', 'TCD', 'TD', 'Chad'],
	['152', 'CHL', 'CL', 'Chile'],
	['156', 'CHN', 'CN', 'China'],
	['158', 'TWN', 'TW', 'Taiwan'],
	['170', 'COL', 'CO', 'Colombia'],
	['174', 'COM', 'KM', 'Comoros'],
	['178', 'COG', 'CG', 'Congo'],
	['180', 'COD', 'CD', 'DR Congo', 'Dem. Rep. Congo'],
	['184', 'COK', 'CK', 'Cook Islands', 'Cook Is.'],
	['188', 'CRI', 'CR', 'Costa Rica'],
	['191', 'HRV', 'HR', 'Croatia'],
	['192', 'CUB', 'CU', 'Cuba'],
	['196', 'CYP', 'CY', 'Cyprus'],
	['203', 'CZE', 'CZ', 'Czechia'],
	['204', 'BEN', 'BJ', 'Benin'],
	['208', 'DNK', 'DK', 'Denmark'],
	['212', 'DMA', 'DM', 'Dominica'],
	['214', 'DOM', 'DO', 'Dominican Republic', 'Dominican Rep.'],
	['218', 'ECU', 'EC', 'Ecuador'],
	['222', 'SLV', 'SV', 'El Salvador'],
	['226', 'GNQ', 'GQ', 'Equatorial Guinea', 'Eq. Guinea'],
	['231', 'ETH', 'ET', 'Ethiopia'],
	['232', 'ERI', 'ER', 'Eritrea'],
	['233', 'EST', 'EE', 'Estonia'],
	['234', 'FRO', 'FO', 'Faroe Islands', 'Faeroe Is.'],
	['238', 'FLK', 'FK', 'Falkland Islands', 'Falkland Is.'],
	['239', 'SGS', 'GS', 'South Georgia', 'S. Geo. and the Is.'],
	['242', 'FJI', 'FJ', 'Fiji'],
	['246', 'FIN', 'FI', 'Finland'],
	['248', 'ALA', 'AX', 'Åland'],
	['250', 'FRA', 'FR', 'France'],
	['258', 'PYF', 'PF', 'French Polynesia', 'Fr. Polynesia'],
	['260', 'ATF', 'TF', 'French Southern Lands', 'Fr. S. Antarctic Lands'],
	['262', 'DJI', 'DJ', 'Djibouti'],
	['266', 'GAB', 'GA', 'Gabon'],
	['268', 'GEO', 'GE', 'Georgia'],
	['270', 'GMB', 'GM', 'Gambia'],
	['275', 'PSE', 'PS', 'Palestine'],
	['276', 'DEU', 'DE', 'Germany'],
	['288', 'GHA', 'GH', 'Ghana'],
	['296', 'KIR', 'KI', 'Kiribati'],
	['300', 'GRC', 'GR', 'Greece'],
	['304', 'GRL', 'GL', 'Greenland'],
	['308', 'GRD', 'GD', 'Grenada'],
	['316', 'GUM', 'GU', 'Guam'],
	['320', 'GTM', 'GT', 'Guatemala'],
	['324', 'GIN', 'GN', 'Guinea'],
	['328', 'GUY', 'GY', 'Guyana'],
	['332', 'HTI', 'HT', 'Haiti'],
	['334', 'HMD', 'HM', 'Heard and McDonald Islands', 'Heard I. and McDonald Is.'],
	['336', 'VAT', 'VA', 'Vatican'],
	['340', 'HND', 'HN', 'Honduras'],
	['344', 'HKG', 'HK', 'Hong Kong'],
	['348', 'HUN', 'HU', 'Hungary'],
	['352', 'ISL', 'IS', 'Iceland'],
	['356', 'IND', 'IN', 'India'],
	['360', 'IDN', 'ID', 'Indonesia'],
	['364', 'IRN', 'IR', 'Iran'],
	['368', 'IRQ', 'IQ', 'Iraq'],
	['372', 'IRL', 'IE', 'Ireland'],
	['376', 'ISR', 'IL', 'Israel'],
	['380', 'ITA', 'IT', 'Italy'],
	['384', 'CIV', 'CI', "Côte d'Ivoire"],
	['388', 'JAM', 'JM', 'Jamaica'],
	['392', 'JPN', 'JP', 'Japan'],
	['398', 'KAZ', 'KZ', 'Kazakhstan'],
	['400', 'JOR', 'JO', 'Jordan'],
	['404', 'KEN', 'KE', 'Kenya'],
	['408', 'PRK', 'KP', 'North Korea'],
	['410', 'KOR', 'KR', 'South Korea'],
	['414', 'KWT', 'KW', 'Kuwait'],
	['417', 'KGZ', 'KG', 'Kyrgyzstan'],
	['418', 'LAO', 'LA', 'Laos'],
	['422', 'LBN', 'LB', 'Lebanon'],
	['426', 'LSO', 'LS', 'Lesotho'],
	['428', 'LVA', 'LV', 'Latvia'],
	['430', 'LBR', 'LR', 'Liberia'],
	['434', 'LBY', 'LY', 'Libya'],
	['438', 'LIE', 'LI', 'Liechtenstein'],
	['440', 'LTU', 'LT', 'Lithuania'],
	['442', 'LUX', 'LU', 'Luxembourg'],
	['446', 'MAC', 'MO', 'Macao'],
	['450', 'MDG', 'MG', 'Madagascar'],
	['454', 'MWI', 'MW', 'Malawi'],
	['458', 'MYS', 'MY', 'Malaysia'],
	['462', 'MDV', 'MV', 'Maldives'],
	['466', 'MLI', 'ML', 'Mali'],
	['470', 'MLT', 'MT', 'Malta'],
	['478', 'MRT', 'MR', 'Mauritania'],
	['480', 'MUS', 'MU', 'Mauritius'],
	['484', 'MEX', 'MX', 'Mexico'],
	['492', 'MCO', 'MC', 'Monaco'],
	['496', 'MNG', 'MN', 'Mongolia'],
	['498', 'MDA', 'MD', 'Moldova'],
	['499', 'MNE', 'ME', 'Montenegro'],
	['500', 'MSR', 'MS', 'Montserrat'],
	['504', 'MAR', 'MA', 'Morocco'],
	['508', 'MOZ', 'MZ', 'Mozambique'],
	['512', 'OMN', 'OM', 'Oman'],
	['516', 'NAM', 'NA', 'Namibia'],
	['520', 'NRU', 'NR', 'Nauru'],
	['524', 'NPL', 'NP', 'Nepal'],
	['528', 'NLD', 'NL', 'Netherlands'],
	['531', 'CUW', 'CW', 'Curaçao'],
	['533', 'ABW', 'AW', 'Aruba'],
	['534', 'SXM', 'SX', 'Sint Maarten'],
	['540', 'NCL', 'NC', 'New Caledonia'],
	['548', 'VUT', 'VU', 'Vanuatu'],
	['554', 'NZL', 'NZ', 'New Zealand'],
	['558', 'NIC', 'NI', 'Nicaragua'],
	['562', 'NER', 'NE', 'Niger'],
	['566', 'NGA', 'NG', 'Nigeria'],
	['570', 'NIU', 'NU', 'Niue'],
	['574', 'NFK', 'NF', 'Norfolk Island'],
	['578', 'NOR', 'NO', 'Norway'],
	['580', 'MNP', 'MP', 'Northern Mariana Islands', 'N. Mariana Is.'],
	['583', 'FSM', 'FM', 'Micronesia'],
	['584', 'MHL', 'MH', 'Marshall Islands', 'Marshall Is.'],
	['585', 'PLW', 'PW', 'Palau'],
	['586', 'PAK', 'PK', 'Pakistan'],
	['591', 'PAN', 'PA', 'Panama'],
	['598', 'PNG', 'PG', 'Papua New Guinea'],
	['600', 'PRY', 'PY', 'Paraguay'],
	['604', 'PER', 'PE', 'Peru'],
	['608', 'PHL', 'PH', 'Philippines'],
	['612', 'PCN', 'PN', 'Pitcairn Islands', 'Pitcairn Is.'],
	['616', 'POL', 'PL', 'Poland'],
	['620', 'PRT', 'PT', 'Portugal'],
	['624', 'GNB', 'GW', 'Guinea-Bissau'],
	['626', 'TLS', 'TL', 'Timor-Leste'],
	['630', 'PRI', 'PR', 'Puerto Rico'],
	['634', 'QAT', 'QA', 'Qatar'],
	['642', 'ROU', 'RO', 'Romania'],
	['643', 'RUS', 'RU', 'Russia'],
	['646', 'RWA', 'RW', 'Rwanda'],
	['652', 'BLM', 'BL', 'Saint Barthélemy', 'St-Barthélemy'],
	['654', 'SHN', 'SH', 'Saint Helena'],
	['659', 'KNA', 'KN', 'Saint Kitts and Nevis', 'St. Kitts and Nevis'],
	['660', 'AIA', 'AI', 'Anguilla'],
	['662', 'LCA', 'LC', 'Saint Lucia'],
	['663', 'MAF', 'MF', 'Saint Martin', 'St-Martin'],
	['666', 'SPM', 'PM', 'Saint Pierre and Miquelon', 'St. Pierre and Miquelon'],
	['670', 'VCT', 'VC', 'Saint Vincent and the Grenadines', 'St. Vin. and Gren.'],
	['674', 'SMR', 'SM', 'San Marino'],
	['678', 'STP', 'ST', 'São Tomé and Príncipe', 'São Tomé and Principe'],
	['682', 'SAU', 'SA', 'Saudi Arabia'],
	['686', 'SEN', 'SN', 'Senegal'],
	['688', 'SRB', 'RS', 'Serbia'],
	['690', 'SYC', 'SC', 'Seychelles'],
	['694', 'SLE', 'SL', 'Sierra Leone'],
	['702', 'SGP', 'SG', 'Singapore'],
	['703', 'SVK', 'SK', 'Slovakia'],
	['704', 'VNM', 'VN', 'Vietnam'],
	['705', 'SVN', 'SI', 'Slovenia'],
	['706', 'SOM', 'SO', 'Somalia'],
	['710', 'ZAF', 'ZA', 'South Africa'],
	['716', 'ZWE', 'ZW', 'Zimbabwe'],
	['724', 'ESP', 'ES', 'Spain'],
	['728', 'SSD', 'SS', 'South Sudan', 'S. Sudan'],
	['729', 'SDN', 'SD', 'Sudan'],
	['732', 'ESH', 'EH', 'Western Sahara', 'W. Sahara'],
	['740', 'SUR', 'SR', 'Suriname'],
	['748', 'SWZ', 'SZ', 'Eswatini', 'eSwatini'],
	['752', 'SWE', 'SE', 'Sweden'],
	['756', 'CHE', 'CH', 'Switzerland'],
	['760', 'SYR', 'SY', 'Syria'],
	['762', 'TJK', 'TJ', 'Tajikistan'],
	['764', 'THA', 'TH', 'Thailand'],
	['768', 'TGO', 'TG', 'Togo'],
	['776', 'TON', 'TO', 'Tonga'],
	['780', 'TTO', 'TT', 'Trinidad and Tobago'],
	['784', 'ARE', 'AE', 'United Arab Emirates'],
	['788', 'TUN', 'TN', 'Tunisia'],
	['792', 'TUR', 'TR', 'Türkiye', 'Turkey'],
	['795', 'TKM', 'TM', 'Turkmenistan'],
	['796', 'TCA', 'TC', 'Turks and Caicos Islands', 'Turks and Caicos Is.'],
	['800', 'UGA', 'UG', 'Uganda'],
	['804', 'UKR', 'UA', 'Ukraine'],
	['807', 'MKD', 'MK', 'North Macedonia', 'Macedonia'],
	['818', 'EGY', 'EG', 'Egypt'],
	['826', 'GBR', 'GB', 'United Kingdom'],
	['831', 'GGY', 'GG', 'Guernsey'],
	['832', 'JEY', 'JE', 'Jersey'],
	['833', 'IMN', 'IM', 'Isle of Man'],
	['834', 'TZA', 'TZ', 'Tanzania'],
	['840', 'USA', 'US', 'United States', 'United States of America'],
	['850', 'VIR', 'VI', 'U.S. Virgin Islands', 'U.S. Virgin Is.'],
	['854', 'BFA', 'BF', 'Burkina Faso'],
	['858', 'URY', 'UY', 'Uruguay'],
	['860', 'UZB', 'UZ', 'Uzbekistan'],
	['862', 'VEN', 'VE', 'Venezuela'],
	['876', 'WLF', 'WF', 'Wallis and Futuna', 'Wallis and Futuna Is.'],
	['882', 'WSM', 'WS', 'Samoa'],
	['887', 'YEM', 'YE', 'Yemen'],
	['894', 'ZMB', 'ZM', 'Zambia'],
	// shapes without an ISO id in Natural Earth
	['n:Kosovo', 'XKX', 'XK', 'Kosovo', 'Kosovo'],
	['n:N. Cyprus', '', '', 'Northern Cyprus', 'N. Cyprus'],
	['n:Somaliland', '', '', 'Somaliland', 'Somaliland'],
	['n:Siachen Glacier', '', '', 'Siachen Glacier', 'Siachen Glacier'],
	['n:Indian Ocean Ter.', '', '', 'Australian Indian Ocean Territories', 'Indian Ocean Ter.'],
];

const ALIASES: Record<string, string[]> = {
	'840': ['usa', 'united states of america', 'america', 'u.s.', 'u.s.a.'],
	'826': ['uk', 'britain', 'great britain', 'u.k.'],
	'180': ['drc', 'democratic republic of the congo', 'congo-kinshasa', 'dem. rep. congo'],
	'178': ['republic of the congo', 'congo-brazzaville'],
	'384': ['ivory coast', "cote d'ivoire"],
	'203': ['czech republic'],
	'807': ['macedonia'],
	'748': ['swaziland'],
	'792': ['turkey', 'turkiye'],
	'104': ['burma'],
	'410': ['korea', 'republic of korea'],
	'408': ['dprk'],
	'643': ['russian federation'],
	'418': ['lao pdr'],
	'704': ['viet nam'],
	'626': ['east timor'],
	'132': ['cape verde'],
	'528': ['holland', 'the netherlands'],
	'784': ['uae', 'emirates'],
	'682': ['ksa'],
	'070': ['bosnia'],
	'275': ['palestinian territories'],
	'336': ['vatican city', 'holy see'],
	'678': ['sao tome and principe'],
	'248': ['aland'],
	'652': ['saint barthelemy'],
	'531': ['curacao'],
	'344': ['hongkong'],
};

// Bangla names (used as aliases, and as labels with lang 'bn').
const BANGLA: Record<string, string> = {
	'050': 'বাংলাদেশ',
	'356': 'ভারত',
	'586': 'পাকিস্তান',
	'524': 'নেপাল',
	'064': 'ভুটান',
	'104': 'মিয়ানমার',
	'144': 'শ্রীলঙ্কা',
	'462': 'মালদ্বীপ',
	'004': 'আফগানিস্তান',
	'156': 'চীন',
	'392': 'জাপান',
	'410': 'দক্ষিণ কোরিয়া',
	'682': 'সৌদি আরব',
	'784': 'সংযুক্ত আরব আমিরাত',
	'634': 'কাতার',
	'414': 'কুয়েত',
	'512': 'ওমান',
	'048': 'বাহরাইন',
	'400': 'জর্ডান',
	'422': 'লেবানন',
	'364': 'ইরান',
	'818': 'মিশর',
	'458': 'মালয়েশিয়া',
	'702': 'সিঙ্গাপুর',
	'360': 'ইন্দোনেশিয়া',
	'764': 'থাইল্যান্ড',
	'826': 'যুক্তরাজ্য',
	'840': 'যুক্তরাষ্ট্র',
	'124': 'কানাডা',
	'036': 'অস্ট্রেলিয়া',
	'554': 'নিউজিল্যান্ড',
	'380': 'ইতালি',
	'250': 'ফ্রান্স',
	'276': 'জার্মানি',
	'643': 'রাশিয়া',
	'792': 'তুরস্ক',
	'076': 'ব্রাজিল',
};

export type CountryInfo = {
	key: string; // the id world-atlas uses ('050'), or 'n:' + its name
	a3: string;
	a2: string;
	name: string; // display name
	atlasName: string; // the name in world-atlas
	nameBn?: string;
};

const norm = (s: string): string => s.trim().toLowerCase().normalize('NFC');

const INFO: CountryInfo[] = ROWS.map(([key, a3, a2, name, atlasName]) => ({
	key,
	a3,
	a2,
	name,
	atlasName: atlasName ?? name,
	nameBn: BANGLA[key],
}));

const BY_KEY = new Map<string, CountryInfo>(INFO.map((c) => [c.key, c]));
const LOOKUP = new Map<string, string>();
for (const c of INFO) {
	for (const k of [c.key, c.a3, c.a2, c.name, c.atlasName, c.nameBn, ...(ALIASES[c.key] ?? [])]) {
		if (k) {
			const n = norm(k);
			if (!LOOKUP.has(n)) {
				LOOKUP.set(n, c.key);
			}
		}
	}
}

/** The world-atlas key of a country ('050' for Bangladesh), or null when nothing matches. */
export const countryKey = (ref: CountryRef): string | null => {
	if (typeof ref === 'number') {
		const id = String(Math.round(ref)).padStart(3, '0');
		return BY_KEY.has(id) ? id : null;
	}
	const n = norm(ref);
	if (/^\d{1,3}$/.test(n)) {
		const id = n.padStart(3, '0');
		return BY_KEY.has(id) ? id : null;
	}
	return LOOKUP.get(n) ?? null;
};

/** Name, codes and Bangla name of a country; null for an unknown reference. */
export const countryInfo = (ref: CountryRef): CountryInfo | null => {
	const k = countryKey(ref);
	return k ? BY_KEY.get(k) ?? null : null;
};

/** The label for a country: its display name, or its Bangla name with lang 'bn' (English when none is known). */
export const countryName = (ref: CountryRef, lang: 'en' | 'bn' = 'en'): string => {
	const c = countryInfo(ref);
	if (!c) {
		return String(ref);
	}
	return lang === 'bn' ? c.nameBn ?? c.name : c.name;
};

/** Every country the lookup knows. */
export const allCountries = (): readonly CountryInfo[] => INFO;

/** Resolves a reference and throws a readable error when it matches nothing (typos surface at once). */
export const requireCountryKey = (ref: CountryRef): string => {
	const k = countryKey(ref);
	if (!k) {
		throw new Error(`maps: no country matches "${ref}". Use a name ('Bangladesh'), an ISO code ('BGD', 'BD') or its numeric id ('050').`);
	}
	return k;
};
