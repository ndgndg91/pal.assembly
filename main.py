import sys
import time
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """
    임시 세션 프로필을 사용하여 브라우저 실행
    """
    chrome_options = Options()
    
    # 매 실행마다 고유한 임시 폴더를 생성하여 Lock 충돌 방지
    temp_dir = tempfile.mkdtemp(prefix="assembly_helper_")
    chrome_options.add_argument(f"user-data-dir={temp_dir}")
    
    # 팝업 알림 무시 설정
    chrome_options.set_capability("unhandledPromptBehavior", "accept")
    
    chrome_options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    })
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    print("[시스템] 브라우저를 실행합니다...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.maximize_window()
    return driver

if __name__ == "__main__":
    tasks = [
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_E2U6T0S3R1X8W1Y3G0F4E3D0J1I0H8", "title": "본 개정안에 반대합니다.", "message": "해당 법안의 문제점이 다수 지적되고 있어 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_T2S6R0Z3Y1X8V1S7R5N0W4V6U6T0B8", "title": "본 개정안에 반대합니다.", "message": "국민적 공감대 형성이 부족한 법안이므로 부결되어야 합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_U2T6T0B2A2A4Y1Z3X5Y8G2G9F4F0E9", "title": "본 개정안에 반대합니다.", "message": "실질적 효과보다 혼란만 초래할 개정안이기에 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_N2U6V0T3U0S5T1R5S0Z9Y5Y0X6X2V5", "title": "본 개정안에 반대합니다.", "message": "다양한 부작용과 문제점이 발생할 수 있어 개정안에 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_N2O6W0W1V2T1U1S4S1H0I2G9H4F5E3", "title": "본 개정안에 반대합니다.", "message": "오히려 상황을 악화시킬 수 있는 법안이므로 강하게 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_W2U6V0U3S0S5A1B6Z4A8Y3Z2X3X9F0", "title": "본 개정안에 반대합니다.", "message": "개정안으로 인한 이점보다 피해가 더 클 것으로 판단되어 반대합니다."}
    ]

    try:
        driver = setup_driver()
        
        # 1. 오직 첫 번째 작업 페이지만 엽니다. (세션 충돌 방지)
        print(f"[시스템] 로그인을 위해 첫 번째 법안 페이지로 이동합니다...")
        driver.get(tasks[0]['url'])
        
        try:
            # 혹시 접속 직후 팝업이 뜨면 닫기
            time.sleep(1)
            driver.switch_to.alert.accept()
        except Exception:
            pass

        print("\n" + "="*60)
        print(" [중요] 열려있는 창에서 로그인을 완료해 주세요!")
        print(" (세션 충돌을 막기 위해 탭을 하나만 열었습니다.)")
        print(" 로그인이 완전히 끝난 후 (의견 등록 페이지가 보이면),")
        print(" 아래 터미널(이 창)에서 아무 키나 누르고 [Enter]를 치세요!")
        print("="*60 + "\n")

        # 파이썬 프로그램 완전 정지
        input(" >>> 로그인을 완료하셨다면 아무 키나 누르고 Enter 키를 치세요: ")

        print(f"\n[시스템] 총 {len(tasks)}개의 법안 세팅을 매우 빠르게 진행합니다...\n")

        # 2. 로그인 완료 후, 순차적으로 새 탭을 열며 작업 수행
        main_handle = driver.current_window_handle
        
        for i, current_task in enumerate(tasks):
            try:
                if i == 0:
                    driver.switch_to.window(main_handle)
                    driver.get(current_task['url'])
                else:
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[-1])
                    driver.get(current_task['url'])
                
                # 속도 향상: 고정 대기시간 대신 WebDriverWait을 사용하여 
                # 의견 등록 폼이 로드되는 즉시 작업을 진행합니다.
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "txt_sj"))
                    )
                except Exception:
                    pass # 타임아웃 되더라도 스크립트 실행은 시도
                
                current_url = driver.current_url
                
                if "forInsert.do" in current_url:
                    script = f"""
                        function setValue(id, val) {{
                            var el = document.getElementById(id);
                            if(el) {{
                                el.value = val;
                                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                return true;
                            }}
                            return false;
                        }}
                        var s1 = setValue('txt_sj', "{current_task['title']}");
                        var s2 = setValue('txt_cn', `{current_task['message']}`);
                        var captcha = document.getElementById('catpchaAnswer');
                        if(captcha) {{
                            captcha.scrollIntoView({{block: 'center'}});
                            captcha.focus();
                            captcha.click();
                        }}
                        return s1 && s2;
                    """
                    if driver.execute_script(script):
                        print(f"[{i+1}/{len(tasks)}] 완료: {current_task['url'].split('lgsltPaId=')[1][:15]}")
                    else:
                        print(f"[{i+1}/{len(tasks)}] 오류: 입력창 없음")
                else:
                    print(f"[{i+1}/{len(tasks)}] 오류: 잘못된 페이지 이동 ({current_url})")
                        
            except Exception as e:
                print(f"[{i+1}/{len(tasks)}] 예외 발생: {e}")

        print("\n" + "="*60)
        print(" [최종 완료] 모든 탭의 세팅이 끝났습니다!")
        print(" 각 탭을 확인하시고, 보안문자만 입력하여 [등록]을 눌러주세요.")
        print("="*60)
        
        while True:
            time.sleep(5)
            # 모든 창이 닫히면 프로그램 종료
            if not driver.window_handles: break

    except KeyboardInterrupt:
        print("\n[시스템] 종료합니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[시스템 오류] {e}")