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
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_O2K6H0G3F1U7T0O9M3L8K3T1Q9P8Y0", "title": "본 개정안에 반대합니다.", "message": "해당 법안의 문제점이 다수 지적되고 있어 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_Q2P6Q0O3O1W6X1V1T0U7S0T1B2B1A5", "title": "본 개정안에 반대합니다.", "message": "국민적 공감대 형성이 부족한 법안이므로 부결되어야 합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_Y2F6G0E3F1D6E1C6D1K5L4K7I9I0H1", "title": "본 개정안에 반대합니다.", "message": "실질적 효과보다 혼란만 초래할 개정안이기에 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_E2E6C0E3C1C6A1J6J1H7I0H1H5F1G8", "title": "본 개정안에 반대합니다.", "message": "다양한 부작용과 문제점이 발생할 수 있어 개정안에 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_H2F6E0N3J1I7R1Q6N1K9J3R0Q1P4O8", "title": "본 개정안에 반대합니다.", "message": "오히려 상황을 악화시킬 수 있는 법안이므로 강하게 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_E2M6M0L3J0K9I1J8E3F3D5E6C1B7B7", "title": "본 개정안에 반대합니다.", "message": "개정안으로 인한 이점보다 피해가 더 클 것으로 판단되어 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_W2W6U0V3T0S9T0A9B4Z5A4Y0Z1X4F5", "title": "본 개정안에 반대합니다.", "message": "법안 통과 시 미칠 파장이 크므로 신중히 폐기되어야 합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_R2R6P0O3P0N9N0V9W2U8V3T8U3S8A6", "title": "본 개정안에 반대합니다.", "message": "사회적 갈등만 키우는 해당 개정안에 대해 반대 의사를 표명합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_L2K6K0S3P1N8Q1Z4X0U1C4C0A1Z4I9", "title": "본 개정안에 반대합니다.", "message": "충분한 협의가 없었던 무리한 법안 추진에 단호히 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_I2G6E0F3N0O9M1N3L5L3J3S1S6Q7R7", "title": "본 개정안에 반대합니다.", "message": "본 개정안의 취지에 동의하기 어려우며 반대 의견을 제출합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_E2F6D0D3L0M9K1I3J5H4I3Q0Q3P8P2", "title": "본 개정안에 반대합니다.", "message": "해당 개정안에 대해 심각한 우려를 표하며 강력히 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_C2A6B0Z3A0Y9Z1V8T2T7S3S8R1R6Z8", "title": "본 개정안에 반대합니다.", "message": "본 법안이 사회에 미칠 부정적 영향을 우려하여 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_J2J6I0I3Q0P9P0N9O2M7N0V5V9U9U1", "title": "본 개정안에 반대합니다.", "message": "불필요한 규제를 양산할 수 있어 개정안 통과를 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_K2K6S0T3R1R6Q1R5P5P3X4W8W4V2V8", "title": "본 개정안에 반대합니다.", "message": "개정안의 부작용이 크다고 생각되어 이에 명확히 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_E2C6D0Y3Z0X9Y1W8V2V8D0D5C1C7B1", "title": "본 개정안에 반대합니다.", "message": "다수 국민의 공감을 얻지 못하는 법안이므로 부결되어야 마땅합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_F2D5E1C1D2L6L1J4K5J2H5H9P5Q0O8", "title": "본 개정안에 반대합니다.", "message": "신중한 검토 없이 발의된 법안으로 생각되어 전면 폐기를 요구합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_G2G6E0F3D0E9C1Y3Y5X3X5W9W1U5V9", "title": "본 개정안에 반대합니다.", "message": "법안이 통과되었을 때의 역기능이 순기능을 압도할 것이 자명하여 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_Q2Y6B0A3X1F7F1D1C4L0K4J5G1M5M1", "title": "본 개정안에 반대합니다.", "message": "현실과 동떨어진 개정안이므로 강력하게 반대 의견을 표합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_V2D6D0B1C3B0Z1Z5H1I5G5H9F5G3E9", "title": "본 개정안에 반대합니다.", "message": "개정안의 무리한 통과에 반대하며 원점 재검토를 촉구합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_W2W6V0V3D1C3C1A5B4Z5A1W7W0V7T6", "title": "본 개정안에 반대합니다.", "message": "입법 취지와 실효성이 의심스러운 법안으로 결사 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_H2G6G0F2F0B2B1A7Y1Z3X2X1F1G3E7", "title": "본 개정안에 반대합니다.", "message": "법안 통과로 인해 야기될 혼란을 고려하여 반대 의견을 제시합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_V2C6D0B2A1A0Z1Z3V4W6U1V2T2T4S2", "title": "본 개정안에 반대합니다.", "message": "해당 개정안은 오히려 관련 문제를 심화시킬 우려가 있어 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_P2Q6O0P3N1O6W0W9U3T3U5S1S7O1O3", "title": "본 개정안에 반대합니다.", "message": "사회적 수용성이 낮은 무리한 입법이므로 강력히 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_T2T6S0A3A1Y6Z1X1I1I9H2I4G6G6C0", "title": "본 개정안에 반대합니다.", "message": "해당 법안의 실익을 찾기 어려워 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_U2Q6Q0O3Q1O3O1M3V2V3T1U2S3T4R4", "title": "본 개정안에 반대합니다.", "message": "부정적 파급 효과가 클 것으로 예측되어 개정안에 반대합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_C2B6Z0Z3Y1Y0N1O7M0N0L3L8K9S2T0", "title": "본 개정안에 반대합니다.", "message": "법안의 통과에 단호히 반대하며, 깊이 있는 숙의를 촉구합니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_K2S6T0R3S1Q6P1P5X2Y2W3W1U1V9U8", "title": "본 개정안에 반대합니다.", "message": "해당 개정안은 국민적 동의를 얻지 못한 무리한 법안입니다."},
        {"url": "https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId=PRC_F2D6E0C3C1K3J1J1I3I5G2H8W4X7V2", "title": "본 개정안에 반대합니다.", "message": "여러 부작용이 우려되는 바, 해당 법안에 명백한 반대 의사를 밝힙니다."}
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