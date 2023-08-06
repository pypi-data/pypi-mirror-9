import requests
import lxml.etree as et
from null_parser import Null_Parser
from json_parser import JSON_Parser

class NSLDS():

    # Class Variables
    host = 'https://www.nslds.ed.gov'
    entry_link = '/nslds_SA/SaPrivacyConfirmation.do'
    accept_link = '/nslds_SA/SaFinPrivacyAccept.do'
    login_link = '/nslds_SA/secure/SaFinLogin.do'
    login_action = '/nslds_SA/secure/SaFinLogin.do'
    loan_download = '/nslds_SA/secure/SaFinShowMyDataConfirm.do'
    download_confirm = '/nslds_SA/secure/MyData/MyStudentData.do'
    system_error_message = 'A system error has occurred'
    file_source ='File Source:U.S. DEPARTMENT OF EDUCATION, NATIONAL STUDENT LOAN DATA SYSTEM (NSLDS)'

    def __init__(self,**kwargs):
        self.borrower_ssn = kwargs.get('borrower_ssn')
        self.borrower_name = kwargs.get('borrower_name')
        self.borrower_dob = kwargs.get('borrower_dob')
        self.pin = kwargs.get('pin')
        self.s = requests.Session()
        self.session_id = None

    def get_parsed_loan_data(self, parser=None):
        loan_data = self.get_loan_data()
        parsed_data = self.parse_loan_data(loan_data, parser)
        return parsed_data

    def parse_loan_data(self, loan_data, parser=Null_Parser()):
        parsed_data = parser.parse_textfile(loan_data)
        return parsed_data

    def login(self):
        # Navigate to Login Page
        login_response = self.s.get(NSLDS.host + NSLDS.login_link)

        # Parse HTML for login page
        login_tree = et.HTML(login_response.content)

        # Get and set sessionId from login page
        input_html_elements = login_tree.findall('.//input')
        for input_element in input_html_elements:
            try:
                name_attr = input_element.attrib['name']
            except KeyError:
                pass
            else:
                if name_attr == 'sessionId':
                    self.session_id=input_element.attrib['value']
        if not self.session_id:
            raise Exception('Unable to find SessionId')

        # Get PIN selection grid
        grid={}
        select_html_elements = login_tree.findall('.//select')
        for select_element in select_html_elements:
            select_name = select_element.attrib['name']+'h'
            grid[select_name]={}
            # Each Select element has 10 options (0-9) that map to PIN selection
            options = select_element.findall('option')
            for option in options:
                val = option.attrib['value']
                pin_num = option.text
                # Creates dict to return grid value for a given real PIN input
                grid[select_name][pin_num]=int(val)

        # Generate parameter list for login POST
        payload = {}
        payload['borrowerSsn'] = self.borrower_ssn
        payload['borrowerName'] = self.borrower_name
        payload['borrowerDob'] = self.borrower_dob
        payload['sessionId'] = self.session_id

        # Uses selection grid to assign correct values for real PIN input
        payload['yin1h']=grid['yin1h'][self.pin[0]]
        payload['yin2h']=grid['yin2h'][self.pin[1]]
        payload['yin3h']=grid['yin3h'][self.pin[2]]
        payload['yin4h']=grid['yin4h'][self.pin[3]]

        # POST login credentials
        post_response = self.s.post(NSLDS.host + NSLDS.login_action, data=payload)

        # Check for login errors
        error_tree = et.HTML(post_response.content)
        errors = error_tree.findall('.//li')
        if errors:
            print 'Encountered following errors while attempting login:'
            for error in errors:
                print error.text
            raise Exception('Login Credential Error')
        return True

    def get_loan_data(self):

        # Login with Creds
        self.login()

        # Download the Loan Data
        click_download_response = self.s.get(NSLDS.host + NSLDS.loan_download)

        confirm_download_response = self.s.get(NSLDS.host + NSLDS.download_confirm, data={'language':'en'})

        loan_data = confirm_download_response.content

        # Check for valid response
        file_source = loan_data.split('\r')[0]
        if NSLDS.system_error_message in file_source:
            raise Exception('NSLDS system error: Your SessionID has Expired')
        elif file_source != NSLDS.file_source:
            raise Exception('Invalid file source: '+file_source)
        else:
            pass

        self.s.close()
        return loan_data
