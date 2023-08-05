# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import types, importlib, time, inspect, os, sys
import log, env, common



def launch_browser():
    
    if env.RUNNING_BROWSER.upper() == "FIREFOX":
        #os.popen("TASKKILL /F /IM firefox.exe")
        
        fp = FirefoxProfile()
        fp.native_events_enabled = False
        
        binary_path = common.get_value_from_conf("FIREFOX_BINARY_PATH")
        
        if binary_path == "":
            env.BROWSER = webdriver.Firefox(firefox_profile=fp)
        else:
            fb = FirefoxBinary(firefox_path=binary_path)
            env.BROWSER = webdriver.Firefox(firefox_profile=fp, firefox_binary=fb)
    
    
    elif env.RUNNING_BROWSER.upper() == "CHROME":
        #os.popen("TASKKILL /F /IM chrome.exe")
        os.popen("TASKKILL /F /IM chromedriver.exe")
        
        binary_path  = common.get_value_from_conf("CHROME_BINARY_PATH")
        chromedriver = common.get_value_from_conf("DRIVER_CHROME")
        
        if binary_path == "":
            os.environ["webdriver.chrome.driver"] = chromedriver
            env.BROWSER = webdriver.Chrome(executable_path=chromedriver)
        else:
            opts = Options()
            opts.binary_location = binary_path
            
            os.environ["webdriver.chrome.driver"] = chromedriver
            env.BROWSER = webdriver.Chrome(executable_path=chromedriver, chrome_options=opts)
    
    
    elif env.RUNNING_BROWSER.upper() == "IE":
        #os.popen("TASKKILL /F /IM iexplore.exe")
        os.popen("TASKKILL /F /IM IEDriverServer.exe")
        
        dc = DesiredCapabilities.INTERNETEXPLORER.copy()
        
        dc['acceptSslCerts'] = True
        dc['nativeEvents']   = True
        
        iedriver = common.get_value_from_conf("DRIVER_IE")
        
        os.environ["webdriver.ie.driver"] = iedriver
        
        env.BROWSER = webdriver.Ie(executable_path=iedriver, capabilities=dc)
    
    
    else:
        return False
    
    
    env.TEST_URL = common.get_value_from_conf("TESTING_URL")
    
    
    env.BROWSER.get(env.TEST_URL)
    env.BROWSER.maximize_window()
    
    time.sleep(3)
    
    return True



def testcase_windingup():
    time.sleep(3)
    env.BROWSER.quit()
    
    os.popen("TASKKILL /F /IM IEDriverServer.exe")
    os.popen("TASKKILL /F /IM chromedriver.exe")




def run_module(module_name):
    if sys.getdefaultencoding() != 'utf-8':
        reload(sys)
        sys.setdefaultencoding('utf-8')
    
    testmodule = importlib.import_module("testcase.%s" % module_name)
    
    env.MODULE_NAME = module_name.split('.')[-1]
    testcases = [testmodule.__dict__.get(a).__name__ for a in dir(testmodule)
           if isinstance(testmodule.__dict__.get(a), types.FunctionType)]
    
    env.PROJECT_PATH = os.path.dirname(os.path.abspath(inspect.stack()[1][1]))
    sys.path.append(env.PROJECT_PATH)
    env.TESTING_BROWSERS = common.get_value_from_conf("TESTING_BROWSERS")
    
    
    for testcase in testcases:
        if testcase == "before_each_testcase" or testcase == "after_each_testcase" or testcase == "before_launch_browser":
            continue
        
        for browser in env.TESTING_BROWSERS.split('|'):
            env.RUNNING_BROWSER = browser
            
            
            ##### Launch Browser
            if "before_launch_browser" in testcases:
                getattr(testmodule, "before_launch_browser")()
            
            if launch_browser() == False:
                continue
            
            
            ##### Run Test Case.
            try:
                log.start_test(testcase)
                
                if "before_each_testcase" in testcases:
                    getattr(testmodule, "before_each_testcase")()
                
                getattr(testmodule, testcase)()
            except:
                log.handle_error()
            finally:
                if "after_each_testcase" in testcases:
                    getattr(testmodule, "after_each_testcase")()
                
                log.stop_test()
            
            
            ##### Clear Environment. Quite Browser, Kill Driver Processes.
            testcase_windingup()





def run_case(module_name, case_name):
    if sys.getdefaultencoding() != 'utf-8':
        reload(sys)
        sys.setdefaultencoding('utf-8')
    
    testmodule = importlib.import_module("testcase.%s" % module_name)
    
    env.MODULE_NAME = module_name.split('.')[-1]
    testcases = [testmodule.__dict__.get(a).__name__ for a in dir(testmodule)
           if isinstance(testmodule.__dict__.get(a), types.FunctionType)]
    
    env.PROJECT_PATH = os.path.dirname(os.path.abspath(inspect.stack()[1][1]))
    sys.path.append(env.PROJECT_PATH)
    env.TESTING_BROWSERS = common.get_value_from_conf("TESTING_BROWSERS")
    
    if not case_name in testcases:
        return
    
    
    
    for browser in env.TESTING_BROWSERS.split('|'):
        env.RUNNING_BROWSER = browser
        
        
        ##### Launch Browser
        if "before_launch_browser" in testcases:
            getattr(testmodule, "before_launch_browser")()
        
        if launch_browser() == False:
            continue
        
        ##### Run Test Case.
        try:
            log.start_test(case_name)
            
            if "before_each_testcase" in testcases:
                getattr(testmodule, "before_each_testcase")()
            
            getattr(testmodule, case_name)()
        except:
            log.handle_error()
        finally:
            if "after_each_testcase" in testcases:
                getattr(testmodule, "after_each_testcase")()
            
            log.stop_test()
        
        
        ##### Clear Environment. Quite Browser, Kill Driver Processes.
        testcase_windingup()







