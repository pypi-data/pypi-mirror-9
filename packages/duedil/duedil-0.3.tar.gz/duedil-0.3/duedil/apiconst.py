# -*- coding: utf-8 -*-
#
#  DuedilApiConstanstants v3
#  @copyright 2014 Christian Ledermann
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
#

# Here are all the terms available in the companies filters parameter.

LOCALE = "locale"  # string
# This terms accepts only the values uk or roi.

LOCATION = "location"  # string
# This term accepts the name of a city and/or the address.

POSTCODE = "postcode"  # string
# This term accepts a valid uk postcode.

SIC_CODE = "sic_code"  # integer
# sic_code. This term accepts only the standard SIC 03 code

SIC_2007_CODE = "sic_2007_code"  # integer
# sic_2007_code. This term accepts only the standard SIC 07 code

STATUS = "status"  # string
# This term accepts only active, dissolved, in receivership or liquidation
# queries.

CURRENCY = "currency"  # float
# This term accepts only the value eur or gbp

KEYWORDS = "keywords"  # string
# Search keywords

NAME = "name"  # string
# The name of the company you’re looking for. This field must be a string.

COMPANY_TERM_FILTERS = [
    LOCALE,
    LOCATION,
    POSTCODE,
    SIC_CODE,
    SIC_2007_CODE,
    STATUS,
    CURRENCY,
    KEYWORDS,
    NAME,
]


# Here are all the ranges available in the filters parameter.
# These ranges must have an integer value.

EMPLOYEE_COUNT = "employee_count"  # string
# Number of people employed by the company. NB: employee numbers not
# available for all companies. As such when searching for employee
# numbers, only companies with this data available will be searched.

TURNOVER = "turnover"  # string
# The income a company receives from normal business activities.
# Internationally known as "revenue".

TURNOVER_DELTA_PERCENTAGE = "turnover_delta_percentage"  # string
# Movement in turnover from previous year’s filing to latest filing.

GROSS_PROFIT = "gross_profit"  # string
# Turnover minus the cost of sales. Gross profit doesn't include
# administrative, financial, or distribution costs.

GROSS_PROFIT_DELTA_PERCENTAGE = "gross_profit_delta_percentage"  # string
# Movement in gross profit from previous year’s filing to latest filing.

COST_OF_SALES = "cost_of_sales"  # string
# Costs attributable to the production of the goods or supply of services.

COST_OF_SALES_DELTA_PERCENTAGE = "cost_of_sales_delta_percentage"  # string
# Movement in cost of sales from previous year’s filing to latest filing.

NET_ASSETS = "net_assets"  # string
# Net assets refers to the value of a company's assets minus its liabilities.

NET_ASSETS_DELTA_PERCENTAGE = "net_assets_delta_percentage"  # string
# percentage change between the latest filing's value and previous
# filing's value of net assets.

CURRENT_ASSETS = "current_assets"  # string
# All assets belonging to a company that can be converted easily into cash
# and are expected to be used (sold or consumed) within a year.

CURRENT_ASSETS_DELTA_PERCENTAGE = "current_assets_delta_percentage"  # string
# The change in the current assets value from the previous year’s filing
# to latest filing.

TOTAL_ASSETS = "total_assets"  # string
# The sum of current and long-term assets owned by the company.

TOTAL_ASSETS_DELTA_PERCENTAGE = "total_assets_delta_percentage"  # string
# The change in the total assets value from previous year’s filing to
# latest filing.

CASH = "cash"  # string
# Included in current assets, cash refers to the amount held in current or
# deposit bank accounts, and is seen as a highly liquid form of current
# asset.

CASH_DELTA_PERCENTAGE = "cash_delta_percentage"  # string
# Movement in cash from previous year’s filing to latest filing.

TOTAL_LIABILITIES = "total_liabilities"  # string
# The total of all debts for which a company is liable; includes
# short-term and long-term liabilities.

# string
TOTAL_LIABILITIES_DELTA_PERCENTAGE = "total_liabilities_delta_percentage"
# The change in the value of total liabilities from previous year’s filing
# to latest filing.

NET_WORTH = "net_worth"  # string
# The amount by which assets exceed liabilities. Net worth is a concept
# applicable to businesses as a measure of how much an entity is worth.

NET_WORTH_DELTA_PERCENTAGE = "net_worth_delta_percentage"  # string
# Movement in net worth from previous year’s filing to latest filing.

DEPRECIATION = "depreciation"  # string
# A decrease in the value of company assets. Depreciation indicates how
# much of an asset's value has been used up.

DEPRECIATION_DELTA_PERCENTAGE = "depreciation_delta_percentage"  # string
# Movement in depreciation from previous year’s filing to latest filing.

TAXATION = "taxation"  # string
# Amount set aside for taxation purposes.

RETAINED_PROFITS = "retained_profits"  # string
# Profit kept in the company rather than paid out to shareholders as a
# dividend.

PROFIT_RATIO = "profit_ratio"  # string
# The profit ratio measures the amount of profit generated by each £1 of
# sales. Calculated as net profit / turnover.

INVENTORY_TURNOVER_RATIO = "inventory_turnover_ratio"  # string
# The number of times the stock is sold and replaced in a year (calculated
# as sales divided by stock).

NET_PROFITABILITY = "net_profitability"  # string
# The amount of sales needed to generate £1 of net profit. Calculated as
# turnover / net profit.

RETURN_ON_CAPITAL_EMPLOYED = "return_on_capital_employed"  # string
# The profit generated as a function of the capital invested in the
# business (calculated as net profit divided by capital employed).

CASH_TO_TOTAL_ASSETS_RATIO = "cash_to_total_assets_ratio"  # string
# The percentage of the company's assets that are held as cash (calculated
# as cash divided by total assets).

GEARING = "gearing"  # string
# The debt to equity ratio in the business (calculated as total long term
# liabilities divided by shareholder equity).

GROSS_MARGIN_RATIO = "gross_margin_ratio"  # string
# The gross profitability generated by the business as a percentage of the
# turnover received before accounting for fixed costs and overheads
# (calculated as gross profit divided by turnover).

RETURN_ON_ASSETS_RATIO = "return_on_assets_ratio"  # string
# The profit generated in a business as a function of the assets held
# (calculated as gross profit divided by total assets).

CURRENT_RATIO = "current_ratio"  # string
# A measure of the company's short term solvency (calculated as current
# assets divided by current liabilities).

DEBT_TO_CAPITAL_RATIO = "debt_to_capital_ratio"  # string
# A measure of the company's leverage (calculated as total liabilities
# divided by the total shareholder equity plus total liabilities).

# string
CASH_TO_CURRENT_LIABILITIES_RATIO = "cash_to_current_liabilities_ratio"
# A measure of the company's ability to meet its short term obligations
# (calculated as cash divided by short term liabilities).

LIQUIDITY_RATIO = "liquidity_ratio"  # string
# A measure of the company's ability to meet short term obligations by
# liquidating certain assets, excluding its stock (calculated as current
# assets less stock divided by current liabilities).

COMPANY_RANGE_FILTERS = [
    EMPLOYEE_COUNT,
    TURNOVER,
    TURNOVER_DELTA_PERCENTAGE,
    GROSS_PROFIT,
    GROSS_PROFIT_DELTA_PERCENTAGE,
    COST_OF_SALES,
    COST_OF_SALES_DELTA_PERCENTAGE,
    NET_ASSETS,
    NET_ASSETS_DELTA_PERCENTAGE,
    CURRENT_ASSETS,
    CURRENT_ASSETS_DELTA_PERCENTAGE,
    TOTAL_ASSETS,
    TOTAL_ASSETS_DELTA_PERCENTAGE,
    CASH,
    CASH_DELTA_PERCENTAGE,
    TOTAL_LIABILITIES,
    TOTAL_LIABILITIES_DELTA_PERCENTAGE,
    NET_WORTH,
    NET_WORTH_DELTA_PERCENTAGE,
    DEPRECIATION,
    DEPRECIATION_DELTA_PERCENTAGE,
    TAXATION,
    RETAINED_PROFITS,
    PROFIT_RATIO,
    INVENTORY_TURNOVER_RATIO,
    NET_PROFITABILITY,
    RETURN_ON_CAPITAL_EMPLOYED,
    CASH_TO_TOTAL_ASSETS_RATIO,
    GEARING,
    GROSS_MARGIN_RATIO,
    RETURN_ON_ASSETS_RATIO,
    CURRENT_RATIO,
    DEBT_TO_CAPITAL_RATIO,
    CASH_TO_CURRENT_LIABILITIES_RATIO,
    LIQUIDITY_RATIO,
]


# This “Director search endpoint” is similar to the “Company search
# endpoint”, though with some different ranges and terms.

# Searching by financial range will return directors who have a
# directorship at a company fulfilling that range.

# NB: The location filter is not available for director search.


NAME = "name"  # string
# This field must be a string that contains the director’s name.

GENDER = "gender"  # string
# This term accepts only the value M or F

TITLE = "title"  # string
# View all available titles.

NATIONALITY = "nationality"  # string
# View all available nationalities.

SECRETARIAL = "secretarial"  # boolean
# This is a boolean field; the values accepted are true or false

CORPORATE = "corporate"  # boolean
# This is a boolean field; the values accepted are true or false

DISQUALIFIED = "disqualified"  # string
# This is a boolean field; the values accepted are true or false

DIRECTOR_TERM_FILTERS = [
    NAME,
    GENDER,
    TITLE,
    NATIONALITY,
    SECRETARIAL,
    CORPORATE,
    DISQUALIFIED,
]


AGE = "age"  # string
# The age brackets of the director

DATA_OF_BIRTH = "data_of_birth"  # dateTime
# The date of birth brackets of the director. The data must be in this
# format MM/DD/YYY

GROSS_PROFIT = "gross_profit"  # float
# Turnover minus the cost of sales. Gross profit doesn't include
# administrative, financial, or distribution costs.

GROSS_PROFIT_DELTA_PERCENTAGE = "gross_profit_delta_percentage"  # string
# Movement in gross profit from previous year’s filing to latest filing.

TURNOVER = "turnover"  # string
# The income a company Receives from normal business activities.
# Internationally known as "revenue".

TURNOVER_DELTA_PERCENTAGE = "turnover_delta_percentage"  # string
# Movement in turnover from previous year’s filing to latest filing.

COST_OF_SALES = "cost_of_sales"  # string
# Costs attributable to the production of the goods or supply of services.

COST_OF_SALES_DELTA_PERCENTAGE = "cost_of_sales_delta_percentage"  # string
# Movement in cost of sales from previous year’s filing to latest filing.

DEPRECIATION = "depreciation"  # string
# A decrease in the value of company assets. Depreciation indicates how
# much of an asset's value has been used up.

DEPRECIATION_DELTA_PERCENTAGE = "depreciation_delta_percentage"  # string
# Movement in depreciation from previous year’s filing to latest filing.

TAXATION = "taxation"  # string
# Amount set aside for taxation purposes.

CASH = "cash"  # string
# Included in current assets, cash refers to the amount held in current or
# deposit bank accounts, and is seen as a highly liquid form of current
# asset.

CASH_DELTA_PERCENTAGE = "cash_delta_percentage"  # string
# Movement in cash from previous year’s filing to latest filing.

NET_WORTH = "net_worth"  # string
# The amount by which assets exceed liabilities. Net worth is a concept
# applicable to businesses as a measure of how much an entity is worth.

NET_WORTH_DELTA_PERCENTAGE = "net_worth_delta_percentage"  # string
# Movement in net worth from previous year’s filing to latest filing.

TOTAL_ASSETS = "total_assets"  # string
# The sum of current and long-term assets owned by the company.

TOTAL_ASSETS_DELTA_PERCENTAGE = "total_assets_delta_percentage"  # string
# The change in the total assets value from previous year’s filing to
# latest filing.

CURRENT_ASSETS = "current_assets"  # string
# All assets belonging to a company that can be converted easily into cash
# and are expected to be used (sold or consumed) within a year.

CURRENT_ASSETS_DELTA_PERCENTAGE = "current_assets_delta_percentage"  # string
# The change in the current assets value from the previous year’s filing
# to latest filing.

NET_ASSETS = "net_assets"  # string
# Net assets refers to the value of a company's assets minus its liabilities.

NET_ASSETS_DELTA_PERCENTAGE = "net_assets_delta_percentage"  # string
# Percentage change between the latest filing's value and previous
# filing's value of net assets.

TOTAL_LIABILITIES = "total_liabilities"  # string
# The total of all debts for which a company is liable; includes
# short-term and long-term liabilities.

# string
TOTAL_LIABILITIES_DELTA_PERCENTAGE = "total_liabilities_delta_percentage"
# The change in the value of total liabilities from previous year’s filing
# to latest filing.

DIRECTOR_RANGE_FILTERS = [
    AGE,
    DATA_OF_BIRTH,
    GROSS_PROFIT,
    GROSS_PROFIT_DELTA_PERCENTAGE,
    TURNOVER,
    TURNOVER_DELTA_PERCENTAGE,
    COST_OF_SALES,
    COST_OF_SALES_DELTA_PERCENTAGE,
    DEPRECIATION,
    DEPRECIATION_DELTA_PERCENTAGE,
    TAXATION,
    CASH,
    CASH_DELTA_PERCENTAGE,
    NET_WORTH,
    NET_WORTH_DELTA_PERCENTAGE,
    TOTAL_ASSETS,
    TOTAL_ASSETS_DELTA_PERCENTAGE,
    CURRENT_ASSETS,
    CURRENT_ASSETS_DELTA_PERCENTAGE,
    NET_ASSETS,
    NET_ASSETS_DELTA_PERCENTAGE,
    TOTAL_LIABILITIES,
    TOTAL_LIABILITIES_DELTA_PERCENTAGE,
]


SERVICE_ADDRESS_ALLOWED_ATTRIBUTES = [
    'id',
    # string
    'last_update',
    # dateTime Date of last update
    'address1',
    # string Address part 1
    'address2',
    # string Address part 2
    'address3',
    # string Address part 3
    'address4',
    # string Address part 4
    'address5',
    # string Address part 5
    'postcode',
    # string Postcode
    'postal_area',
    # string Area code
]

REGISTERED_ADDRESS_ALLOWED_ATTRIBUTES = [
    'id',
    # string The registered ID of the company
    'last_update',
    # dateTime Date of last update
    'company',
    # string Company registration number
    'address1',
    # string Address part 1
    'address2',
    # string Address part 2
    'address3',
    # string Address part 3
    'address4',
    # string Address part 4
    'postcode',
    # string Postcode
    'phone',
    # string phone number
    'tps',
    # string TPS
    'website',
    # string Website
    'po_box',
    # string PO box number
    'care_of',
    # string Care of
    'email',
    # string Email address
    'area_code',
    # string Area code
]

DIRECTORSHIPS_ALLOWED_ATTRIBUTES = [
    'id',
    # string Director ID
    'last_update',
    # dateTime Date last updated
    'active',
    # boolean Active (true/false)
    'status',
    # string Status
    'founding',
    # boolean Founding director (true/false)
    'appointment_date',
    # dateTime Date appointed
    'function',
    # string Function
    'function_code',
    # integer Function code
    'position',
    # string Position
    'position_code',
    # string Position code
    'companies_url',
    # string Link to companies
    'directors_uri',
    # string Link to director profile
    'service_address_uri',
    # string Link to service address
    'address1',
    # string Address line 1
    'address2',
    # string Address line 2
    'address3',
    # string Address line 3
    'address4',
    # string Address line 4
    'address5',
    # string Address line 5
    'postal_area',
    # string Postal area
    'postcode',
    # string Postcode
    # undocumented:
    'owning_company',
    'resignation_date',
    'secretary',
]

DIRECTOR_ALLOWED_ATTRIBUTES = [
    'id',
    # string Director ID
    'last_update',
    # dateTime Date last updated
    'open_directorships_count',
    # integer Number of open directorships
    'open_trading_directorships_count',
    # integer Number of open trading directorships
    'open_trading_director_directorships_count',
    # integer Of which a director
    'open_trading_secretary_directorships_count',
    # integer Of which a secretary
    'closed_directorships_count',
    # integer Number of closed directorships
    'retired_directorships_count',
    # integer Number of retired directorships
    'director_directorships_count',
    # integer Number of directorships (director)
    'open_director_directorships_count',
    # integer Number of open directorships (director)
    'closed_director_directorships_count',
    # integer Number of closed directorships (director)
    'secretary_directorships_count',
    # integer Number of secretary directorships
    'open_secretary_directorships_count',
    # integer Number of open secretary directorships
    'closed_secretary_directorships_count',
    # integer Number of closed secretary directorships
    'retired_secretary_directorships_count',
    # integer Number of retired decretary directorships
    'forename',
    # string Forename
    'surname',
    # string Surname
    'date_of_birth',
    # dateTime Date of Birth
    'directorships_url',
    # string Link to directorships
    'companies_url',
    # string Link to companies
    'director_url',
    # string Link to director profile
    # undocumented:
    'middle_name',
    'title',
    'postal_title',
    'nationality',
    'nation_code',
]

COMPANY_ALLOWED_ATTRIBUTES = [
    'id',
    # 'id' is filled by __init__ and must match this value
    # integer The registered company number (ID) of the company
    'last_update',
    # dateTime Date last updated
    'name',
    # string The registered company name
    'description',
    # string A description of the company filed with the registrar
    'status',
    # string The status of the company
    'incorporation_date',
    # dateTime The date the company was incorporated
    'latest_annual_return_date',
    # dateTime Date of most recent annual return
    'latest_accounts_date',
    # dateTime Date of most recent filed accounts
    'company_type',
    # string The company type
    'accounts_type',
    # string Type of accounts
    'sic_code',
    # integer Standard Industry Classification (SIC) code
    'previous_company_names_url',
    # string Link to previous company names
    'shareholdings_url',
    # string Link to shareholders information
    'accounts_account_status',
    # integer Accounts status
    'accounts_accounts_format',
    # integer Accounts format
    'accounts_assets_current',
    # integer Current assets
    'accounts_assets_intangible',
    # integer Intangible assets
    'accounts_assets_net',
    # integer Net assets
    'accounts_assets_other_current',
    # integer Other current assets
    'accounts_assets_tangible',
    # integer Tangible assets
    'accounts_url',
    # string Link to company accounts
    'accounts_assets_total_current',
    # integer Total current assets
    'accounts_assets_total_fix',
    # integer Total fixed assets
    'accounts_audit_fees',
    # integer Audit fees
    'accounts_bank_overdraft',
    # integer Bank overdraft
    'accounts_bank_overdraft_lt_loans',
    # integer Bank overdraft & long term loans
    'accounts_capital_employed',
    # integer Capital employed
    'accounts_cash',
    # integer Cash
    'accounts_consolidated',
    # boolean Accounts consolidated (Y/N)
    'accounts_cost_of_sales',
    # integer Cost of sales
    'accounts_currency',
    # string Accounts currency
    'accounts_date',
    # dateTime Accounts date
    'accounts_depreciation',
    # integer Depreciation
    'accounts_directors_emoluments',
    # integer Directors' emoluments
    'accounts_dividends_payable',
    # integer Dividends payable
    'accounts_gross_profit',
    # integer Gross profit
    'accounts_increase_in_cash',
    # integer Increase in cash
    'accounts_interest_payments',
    # integer Interest payments
    'accounts_liabilities_current',
    # integer Current liabilities
    'accounts_liabilities_lt',
    # integer Long term liabilities
    'accounts_liabilities_misc_current',
    # integer Miscellaneous current liabilities
    'accounts_liabilities_total',
    # integer Total liabilities
    'accounts_lt_loans',
    # integer Long term loans
    'accounts_months',
    # integer Months included in accounts
    'accounts_net_cashflow_before_financing',
    # integer Net cashflow before financing
    'accounts_net_cashflow_from_financing',
    # integer Net cashflow from financing
    'accounts_net_worth',
    # integer Net worth
    'accounts_no_of_employees',
    # integer Number of employees
    'accounts_operating_profits',
    # integer Operating profits
    'accounts_operations_net_cashflow',
    # integer Net cashflow
    'accounts_paid_up_equity',
    # integer Paid-up equity
    'accounts_pandl_account_reserve',
    # integer Account reserve
    'accounts_pre_tax_profit',
    # integer Pre-tax profit
    'accounts_profit_after_tax',
    # integer Profit after tax
    'accounts_retained_profit',
    # integer Retained profit
    'accounts_shareholder_funds',
    # integer Shareholder funds
    'accounts_short_term_loans',
    # integer Short term loans
    'accounts_stock',
    # integer Stock
    'accounts_sundry_reserves',
    # integer Sundry reserves
    'accounts_taxation',
    # integer Taxation
    'accounts_trade_creditors',
    # integer Trade creditors
    'accounts_turnover',
    # integer Turnover
    'accounts_wages',
    # integer Wages
    'accounts_working_capital',
    # integer Working capital
    'directors_url',
    # string Link to company directors
    'directorships_url',
    # string Link to directorships
    'directorships_open',
    # integer Number of open directorships
    'directorships_open_secretary',
    # integer Number of current directorships with Company Secretary status
    'directorships_open_director',
    # integer Number of current directorships with Director status
    'directorships_retired',
    # integer Number of retired directorships
    'directorships_retired_secretary',
    # integer Of which secretaries
    'directorships_retired_director',
    # integer Of which directors
    'subsidiaries_url',
    # string Link to company subsidiaries
    'documents_url',
    # string Link to original company documents
    'accounts_filing_date',
    # dateTime Accounts filing date
    'ftse_a',
    # integer FTSE listing category
    'mortgage_partial_outstanding_count',
    # integer Number of partially outstanding mortgages
    'mortgage_partial_property_satisfied_count',
    # integer Number of partially satified mortgages
    'mortgage_partial_property_count',
    # integer Number of partial mortgages
    'mortgages_url',
    # string Link to mortgages
    'mortgages_outstanding_count',
    # integer Number of outstanding mortgages
    'mortgages_satisfied_count',
    # integer Number of satisfied mortgages
    'reg_address1',
    # string Registered address street
    'reg_address2',
    # string Registered address town
    'reg_address3',
    # string Registered address county
    'reg_address4',
    # string Registered address country
    'reg_address_postcode',
    # string Registered address postcode
    'reg_area_code',
    # string Registered address area code
    'reg_phone',
    # string Registered phone number
    'reg_tps',
    # boolean Telephone Preference Service (TPS) notification (Y/N)
    'reg_web',
    # string Registered web address
    'sic2007code',
    # integer 2007 Standard Industry Classification (SIC) code
    'trading_address1',
    # string Trading address street
    'trading_address2',
    # string Trading address town
    'trading_address3',
    # string Trading address county
    'trading_address_postcode',
    # string Trading address postcode

    # in addition to the above values I found the following:
    'charity_number',
    'liquidation_status',
    'directorships_closed_director',
    'sic_description',
    'sic_codes_count',
    'trading_address4',
    'directorships_closed',
    'credit_rating_latest_description',
    'accounts_trade_debtors',
    'directorships_closed_secretary',
    'accounts_accountants',
    'accounts_auditors',
    'accounts_contingent_liability',
    'accounts_exports',
    'accounts_qualification_code',
    'accounts_revaluation_reserve',
    'accounts_solicitors',
    'bank_accounts_url',
    'next_annual_return_date',
    'preference_shareholdings_count',
    'preference_shares_issued',
    'reg_address_town',
    'reg_address_towncode',
    'reg_care_of',
    'reg_email',
    'trading_phone',
    'trading_phone_std',
    # from the search we also get:
    'company_url',
    'turnover',
    'turnover_delta_percentage',
    'voluntary_agreement',
]
