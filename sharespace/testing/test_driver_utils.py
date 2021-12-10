import selenium.common.exceptions
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def go_to_profile(username):
    return "http://127.0.0.1:8000/sharespace/user/{}/".format(username)


class TestDriverChrome():

    def __init__(self, path):
        self.driver = webdriver.Chrome(executable_path=path)
        self.home = "http://127.0.0.1:8000/sharespace/"
        self.add_item = "http://127.0.0.1:8000/sharespace/add_item/"
        self.add_pp = "http://127.0.0.1:8000/sharespace/purchase/submit/"

    def login(self, email:str, psw: str):
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
        self.go_home()
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
        select2.select_by_value("2")
        adr = driver.find_element(By.ID, 'id_adr_line_1')
        adr.send_keys(info['adr'])
        phone = driver.find_element(By.ID, 'phone')
        phone.send_keys(info['phone'])
        sub_btn = driver.find_element(By.ID, 'submit-item-btn')
        sub_btn.click()
        driver.implicitly_wait(5)
        tokens = driver.current_url.split("/")
        item_id = tokens[5][5:]
        return item_id

    def add_item_mul_owners(self, info: dict):
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
        select2.select_by_value("2")
        adr = driver.find_element(By.ID, 'id_adr_line_1')
        adr.send_keys(info['adr'])
        owner = driver.find_element(By.ID, info['owner'])
        owner.click()
        _id = "guardian--" + info['guardian']
        guar = driver.find_element(By.ID, _id)
        guar.click()
        phone = driver.find_element(By.ID, 'phone')
        phone.send_keys(info['phone'])
        sub_btn = driver.find_element(By.ID, 'submit-item-btn')
        sub_btn.click()
        driver.implicitly_wait(5)
        tokens = driver.current_url.split("/")
        item_id = tokens[5][5:]
        return item_id

    def borrow_item_test(self, item_name, now_date:str, until_date:str, username:str):
        driver_1 = self.driver
        driver_1.get("http://127.0.0.1:8000/")
        driver_1.implicitly_wait(3)

        src_box = driver_1.find_element(By.ID, 'search_input')
        src_box.send_keys(item_name)
        src_btn = driver_1.find_element(By.ID, 'search-btn')
        src_btn.click()
        driver_1.implicitly_wait(3)
        result = driver_1.find_elements(By.CLASS_NAME, 'src-result')
        print(result)
        result[0].click()
        driver_1.implicitly_wait(3)
        btn = driver_1.find_element(By.ID, 'borrow-item-btn')
        btn.click()
        driver_1.implicitly_wait(3)
        date_out = driver_1.find_element(By.ID, 'date-borrow-from')
        date_out.send_keys(now_date)
        date_in = driver_1.find_element(By.ID, 'date-borrow-until')
        date_in.send_keys(until_date)
        btn = driver_1.find_element(By.ID, 'submit-loan-btn')
        btn.click()
        wait = WebDriverWait(driver_1, 10)
        msg = wait.until(EC.text_to_be_present_in_element((By.ID, 'msg-p') , "loan created"))
        print(msg)
        if not msg:
            return {'loan_created': False, 'loan_id': None}

        else:
            self.driver.get(go_to_profile(username))
            loans = driver_1.find_elements(By.CLASS_NAME, 'user-loan')
            loans[0].click()
            print(driver_1.current_url)
            tokens = driver_1.current_url.split("/")
            loan_id = tokens[5][5:]
            print(loan_id)
            return {'loan_created': True, 'loan_id': loan_id}




    def item_on_loan_pickup_test(self, username):
        driver_here = self.driver
        driver_here.get(go_to_profile(username))
        loans = driver_here.find_elements(By.CLASS_NAME, 'user-loan')
        loans[0].click()
        print(driver_here.current_url)
        tokens = driver_here.current_url.split("/")
        loan_id = tokens[5][5:]
        print(loan_id)
        btn = driver_here.find_element(By.ID, 'confirm-pickup-btn')
        btn.click()
        return loan_id

    def borrower_return_loan_test(self, username):
        driver_1 = self.driver
        driver_1.get("http://127.0.0.1:8000/")
        driver_1.get(go_to_profile(username))
        loans = driver_1.find_elements(By.CLASS_NAME, 'user-loan')
        loans[0].click()
        driver_1.implicitly_wait(5)
        print(driver_1.current_url)
        tokens = driver_1.current_url.split("/")
        loan_id = tokens[5][5:]
        print(loan_id)
        btn = driver_1.find_element(By.ID, 'returned-item-btn')
        btn.click()
        return loan_id

    def loan_confirm_lender(self, username):
        try:

            driver_1 = self.driver
            driver_1.get("http://127.0.0.1:8000/")
            driver_1.get(go_to_profile(username))
            notif = driver_1.find_elements(By.CLASS_NAME, 'user-notification')
            notif[1].click()
            driver_1.implicitly_wait(5)
            select = Select(driver_1.find_element(By.ID, 'action-desired-selection'))
            select.select_by_index(0)
            curr_url = driver_1.current_url
            tokens = curr_url.split("/")
            print(tokens)
            notif_slug = tokens[-2]
            print(notif_slug)
            btn = driver_1.find_element(By.ID, 'action-notif')
            btn.click()
            return {'confirm': True, 'notif_slug': notif_slug}

        except selenium.common.exceptions:
            return {'confirm': False, 'notif_slug': None}

    def cancel_booking_test(self, username):
        try:
            driver = self.driver
            driver.get("http://127.0.0.1:8000/")
            driver.get(go_to_profile(username))
            loans = driver.find_elements(By.CLASS_NAME, 'user-loan')
            loans[0].click()
            driver.implicitly_wait(5)
            print(driver.current_url)
            tokens = driver.current_url.split("/")
            loan_id = tokens[5][5:]
            print(loan_id)
            btn = driver.find_element(By.ID, 'cancel-booking-btn')
            btn.click()
            driver.implicitly_wait(8)
            alert = driver.switch_to.alert
            alert.accept()

            return {'cancelled': True, 'loan_id': loan_id}
        except selenium.common.exceptions:
            return {'cancelled': False, 'loan_id': None}

    def add_pp_test(self, pp_info:dict):
        self.go_add_pp()
        self.driver.implicitly_wait(5)
        print(pp_info)
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

            print(driver.current_url)

            tokens = driver.current_url.split("/")
            prop_slug = tokens[-2]

            return {'pp_created': True, 'pp_id': prop_slug}


        except selenium.common.exceptions:
            return {'pp_created': False, 'pp_id': None}


    def close_driver(self):
        self.driver.close()

    def go_home(self):
        self.driver.get(self.home)

    def go_add_item_page(self):
        self.driver.get(self.add_item)

    def go_add_pp(self):
        self.driver.get(self.add_pp)