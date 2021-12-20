import selenium.common.exceptions
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service



class TestDriver():

    def __init__(self, driver):
        self.home = "http://127.0.0.1:8000/sharespace/"
        self.add_item = "http://127.0.0.1:8000/sharespace/add_item/"
        self.add_pp = "http://127.0.0.1:8000/sharespace/purchase/submit/"
        self.profile = "http://127.0.0.1:8000/sharespace/user/"
        self.driver = driver

    def login(self, email: str, psw: str):
        self.go_home()
        login_link = self.driver.find_element(By.ID, "login-link")
        login_link.click()
        self.driver.implicitly_wait(3)
        email_input = self.driver.find_element(By.ID, "id_username")
        email_input.send_keys(email)
        pass_input = self.driver.find_element(By.ID, 'id_password')
        pass_input.send_keys(psw)
        btn = self.driver.find_element(By.ID, 'login-btn')
        btn.click()

    def add_item_one_owner(self, info: dict):
        try:
            self.add_item_basic(info)
            driver = self.driver
            sub_btn = driver.find_element(By.ID, 'submit-item-btn')
            sub_btn.click()
            driver.implicitly_wait(5)
            tokens = driver.current_url.split("/")
            item_id = tokens[5][5:]
            return {'added': True, 'item_id': item_id}
        except selenium.common.exceptions.NoSuchElementException:
            return {'added': False, 'item_id': None}

    def add_item_mul_owners(self, info: dict):
        try:
            self.add_item_basic(info)
            driver = self.driver
            owner = driver.find_element(By.ID, info['owner'][1])
            owner.click()
            _id = "guardian--" + info['guardian']
            guar = driver.find_element(By.ID, _id)
            guar.click()
            sub_btn = driver.find_element(By.ID, 'submit-item-btn')
            sub_btn.click()
            driver.implicitly_wait(5)
            tokens = driver.current_url.split("/")
            item_id = tokens[5][5:]
            return {'added': True, 'item_id': item_id}
        except selenium.common.exceptions.NoSuchElementException:
            return {'added': False, 'item_id': None}

    def borrow_item_test(self, item_name, now_date: str, until_date: str, username: str):
        try:
            driver_1 = self.driver
            driver_1.get("http://127.0.0.1:8000/")
            driver_1.implicitly_wait(3)

            src_box = driver_1.find_element(By.ID, 'search_input')
            src_box.send_keys(item_name)
            src_btn = driver_1.find_element(By.ID, 'search-btn')
            src_btn.click()
            driver_1.implicitly_wait(3)
            result = driver_1.find_elements(By.CLASS_NAME, 'src-result')

            result[-1].click()
            driver_1.implicitly_wait(3)
            btn = driver_1.find_element(By.ID, 'borrow-item-btn')
            btn.click()
            driver_1.implicitly_wait(3)
            date_out = driver_1.find_element(By.ID, 'date-borrow-from')

            print("\nin driver class, date out input: ", now_date, "\n")
            date_out.send_keys(now_date)
            date_in = driver_1.find_element(By.ID, 'date-borrow-until')

            print("\nin driver class, date in input: ", until_date, '\n')
            date_in.send_keys(until_date)
            btn = driver_1.find_element(By.ID, 'submit-loan-btn')
            print(btn)
            btn.click()
            wait = WebDriverWait(driver_1, 10)
            msg = wait.until(EC.text_to_be_present_in_element((By.ID, 'msg-p'), "loan created"))
            if not msg:
                return {'loan_created': False, 'loan_id': None}

            else:
                self.go_to_profile()
                loans = driver_1.find_elements(By.CLASS_NAME, 'user-loan')
                loans[-1].click()
                tokens = driver_1.current_url.split("/")
                loan_id = tokens[5][5:]
                return {'loan_created': True, 'loan_id': loan_id}
        except selenium.common.exceptions.NoSuchElementException:
            print("not finding button")
            return {'loan_created': False, 'loan_id': None}

    def item_on_loan_pickup_test(self, username):
        try:
            driver_here = self.driver
            self.get_user_latest_loan(username)
            tokens = driver_here.current_url.split("/")
            loan_id = tokens[5][5:]
            btn = driver_here.find_element(By.ID, 'confirm-pickup-btn')
            driver_here.execute_script("arguments[0].scrollIntoView();", btn)
            driver_here.implicitly_wait(5)
            btn.click()
            driver_here.implicitly_wait(5)
            try:
                driver_here.switch_to.alert.accept()
                print("accepted alert")
                return {'loan_picked_up': True, 'loan_id': loan_id}
            except selenium.common.exceptions.NoAlertPresentException:
                print("cannot find alert")
                print("trying to refresh page")
                driver_here.refresh()
                driver_here.implicitly_wait(5)
                return {'loan_picked_up': True, 'loan_id': loan_id}
        except selenium.common.exceptions.NoSuchElementException:
            return {'loan_picked_up': False, 'loan_id': None}

    def borrower_return_loan_test(self, username):
        try:
            driver_1 = self.driver
            self.get_user_latest_loan(username)
            driver_1.implicitly_wait(5)
            tokens = driver_1.current_url.split("/")
            loan_id = tokens[5][5:]
            btn = driver_1.find_element(By.ID, 'returned-item-btn')
            driver_1.execute_script("arguments[0].scrollIntoView();", btn)
            driver_1.implicitly_wait(5)
            btn.click()
            driver_1.implicitly_wait(5)
            driver_1.refresh()
            driver_1.implicitly_wait(6)
            return {'loan_returned': True, 'loan_id': loan_id}
        except selenium.common.exceptions.NoSuchElementException:
            return {'loan_returned': False, 'loan_id': None}


    def loan_confirm_lender(self, username):
        try:

            driver_1 = self.driver
            self.get_user_latest_notification(username)
            driver_1.implicitly_wait(5)
            select = Select(driver_1.find_element(By.ID, 'action-desired-selection'))
            select.select_by_index(0)
            curr_url = driver_1.current_url
            tokens = curr_url.split("/")
            notif_slug = tokens[-2]
            btn = driver_1.find_element(By.ID, 'action-notif')
            btn.click()
            return {'confirm': True, 'notif_slug': notif_slug}

        except selenium.common.exceptions.NoSuchElementException:
            return {'confirm': False, 'notif_slug': None}

    def cancel_booking_test(self, username):
        try:
            driver = self.driver
            self.get_user_latest_loan(username)
            driver.implicitly_wait(5)
            tokens = driver.current_url.split("/")
            loan_id = tokens[5][5:]
            btn = driver.find_element(By.ID, 'cancel-booking-btn')
            btn.click()
            driver.implicitly_wait(10)
            try:
                wait = WebDriverWait(driver, 10)
                wait.until(EC.alert_is_present())
                try:
                    driver.switch_to.alert.accept()
                    driver.implicitly_wait(10)
                    return {'cancelled': True, 'loan_id': loan_id}
                except selenium.common.exceptions.NoAlertPresentException:
                    print("cannot see alert")
                    return {'cancelled': False, 'loan_id': loan_id}
            except selenium.common.exceptions.TimeoutException:
                return {'cancelled': False, 'loan_id': loan_id}
        except selenium.common.exceptions.NoSuchElementException:
            print("cannot find button")
            return {'cancelled': False, 'loan_id': None}

    def add_pp_test(self, pp_info: dict):
        self.go_add_pp()
        self.driver.implicitly_wait(5)
        try:
            driver = self.driver
            name_input = driver.find_element(By.ID, 'id_proposal_item_name')
            descr_input = driver.find_element(By.ID, 'id_proposal_item_description')
            name_input.send_keys(pp_info['name'])
            descr_input.send_keys(pp_info['descr'])
            driver.implicitly_wait(5)
            cat_sel = Select(driver.find_element(By.ID, 'id_proposal_cat'))

            price_input = driver.find_element(By.ID, 'id_proposal_price')
            phone_input = driver.find_element(By.ID, 'id_proposal_contact')
            price_input.send_keys(pp_info['price'])
            phone_input.send_keys(pp_info['phone'])

            cat_sel.select_by_visible_text(pp_info['cat'])
            driver.implicitly_wait(5)
            sub_cat_sel = Select(driver.find_element(By.ID, 'id_proposal_sub_cat'))
            sub_cat_sel.select_by_visible_text(pp_info['sub_cat'])

            btn = driver.find_element(By.ID, 'submit-pp-btn')
            btn.click()

            driver.implicitly_wait(10)

            tokens = driver.current_url.split("/")
            prop_slug = tokens[-2]

            return {'pp_created': True, 'pp_id': prop_slug}

        except selenium.common.exceptions:
            return {'pp_created': False, 'pp_id': None}

    def sub_to_pp_test(self):
        try:
            driver = self.driver
            self.go_home()
            link = driver.find_element(By.ID, 'pp-base-link')
            link.click()
            pp_list = driver.find_elements(By.CLASS_NAME, 'pp-list-elem')
            pp = pp_list[-1]
            pp.click()
            driver.implicitly_wait(5)
            btn = driver.find_element(By.ID, 'subscribe-btn')
            btn.click()
            driver.implicitly_wait(5)
            tokens = driver.current_url.split("/")
            prop_slug = tokens[-2]
            return {'subed': True, 'prop_slug': prop_slug}
        except selenium.common.exceptions:
            return {'subed': False, 'prop_slug': None}

    def unsub_pp_test(self, username):
        try:
            driver = self.driver
            self.go_to_profile()
            subs_list = driver.find_elements(By.CLASS_NAME, 'user-subs')
            pp = subs_list[-1]
            pp.click()
            driver.implicitly_wait(5)
            btn = driver.find_element(By.ID, 'subscribe-btn')
            btn.click()
            driver.implicitly_wait(5)
            tokens = driver.current_url.split("/")
            prop_slug = tokens[-2]
            return {'unsubed': True, 'prop_slug': prop_slug}

        except selenium.common.exceptions:
            return {'unsubed': False, 'prop_slug': None}

    def delete_pp(self, username):
        try:
            driver = self.driver
            self.go_to_profile()
            pp_list = driver.find_elements(By.CLASS_NAME, 'user-pp')
            pp = pp_list[-1]
            pp.click()
            driver.implicitly_wait(5)
            tokens = driver.current_url.split("/")
            prop_slug = tokens[-2]
            btn = driver.find_element(By.ID, 'delete-prop-btn')
            btn.click()
            driver.implicitly_wait(1)
            try:
                wait = WebDriverWait(driver, 10)
                wait.until(EC.alert_is_present())
                try:
                    driver.switch_to.alert.accept()
                    driver.implicitly_wait(10)
                    return {'pp_del': True, 'pp_slug': prop_slug}
                except selenium.common.exceptions.NoAlertPresentException:
                    print("cannot see alert")
                    return {'pp_del': False, 'pp_slug': prop_slug}
            except selenium.common.exceptions.TimeoutException:
                return {'pp_del': False, 'loan_id': prop_slug}
        except selenium.common.exceptions.NoSuchElementException:
            print("cannot find button")
            return {'pp_del': False, 'pp_slug': None}

    def loan_confirm_lender_report(self, username):
        try:
            driver_1 = self.driver
            self.get_user_latest_notification(username)
            driver_1.implicitly_wait(5)
            select = Select(driver_1.find_element(By.ID, 'action-desired-selection'))
            select.select_by_index(1)
            curr_url = driver_1.current_url
            tokens = curr_url.split("/")
            notif_slug = tokens[-2]
            btn = driver_1.find_element(By.ID, 'action-notif')
            btn.click()
            driver_1.implicitly_wait(5)
            title = driver_1.find_element(By.ID, 'id_report_title')
            title.send_keys("testreport")
            body = driver_1.find_element(By.ID, 'id_report_body')
            body.send_keys('testreportbody')
            btn = driver_1.find_element(By.ID, 'submit-report-btn')
            btn.click()
            driver_1.implicitly_wait(5)
            msg_p = driver_1.find_element(By.ID, 'outcome-msg-p')
            text = msg_p.text
            return {'confirm': True, 'reported': True, 'notif_slug': notif_slug, 'text': text}

        except selenium.common.exceptions:
            return {'confirm': False, 'notif_slug': None}

    def close_driver(self):
        self.driver.close()

    def go_home(self):
        self.driver.maximize_window()
        self.driver.get(self.home)

    def go_add_item_page(self):
        self.driver.maximize_window()
        self.driver.get(self.add_item)

    def go_add_pp(self):
        self.driver.maximize_window()
        self.driver.get(self.add_pp)

    def get_user_latest_loan(self, username):
        self.driver.maximize_window()
        driver_here = self.driver
        self.go_to_profile()
        loans = driver_here.find_elements(By.CLASS_NAME, 'user-loan')
        loans[-1].click()

    def get_user_latest_notification(self, username):
        self.driver.maximize_window()
        driver_1 = self.driver
        self.go_to_profile()
        notif = driver_1.find_elements(By.CLASS_NAME, 'user-notification')
        notif[-1].click()

    def add_item_basic(self, info):
        self.driver.maximize_window()
        self.go_add_item_page()
        driver = self.driver
        driver.implicitly_wait(5)
        name = driver.find_element(By.ID, 'id_name')
        name.send_keys(info['name'])
        description = driver.find_element(By.ID, 'id_description')
        description.send_keys(info['description'])
        select = Select(driver.find_element(By.ID, 'main_category'))
        select.select_by_visible_text('Kitchen')
        driver.implicitly_wait(10)
        select1 = Select(driver.find_element(By.ID, 'sec_category'))
        select1.select_by_index(1)
        select2 = Select(driver.find_element(By.ID, 'id_max_loan_len'))
        select2.select_by_value("3")
        adr = driver.find_element(By.ID, 'id_adr_line_1')
        adr.send_keys(info['adr'])
        phone = driver.find_element(By.ID, 'phone')
        phone.send_keys(info['phone'])

    def go_to_profile(self):
        self.driver.maximize_window()
        self.driver.get(self.profile)


class TestDriverChrome(TestDriver):
    def __init__(self):
        service = Service(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        super().__init__(driver)


class TestDriverFirefox(TestDriver):
    def __init__(self):
        service = Service(executable_path=GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service)
        super().__init__(driver)


class TestDriverME(TestDriver):
    def __init__(self):
        service = Service(executable_path="C:\\Users\\chpas\\py-workspace\\sharespace_project\\sharespace\\testing\\drivers\\msedgedriver.exe")
        driver = webdriver.Edge(service=service)
        super().__init__(driver)