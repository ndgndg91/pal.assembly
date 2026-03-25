import sys
import time
import tempfile
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import fetch_links

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

def toggle_bill_status(task):
    """
    법안의 찬성/반대 상태를 토글(반전)합니다.
    """
    if task['is_good']:
        task['is_good'] = False
        task['title'] = "본 개정안에 반대합니다."
        task['message'] = "해당 법안의 문제점이 우려되어 명확히 반대합니다."
    else:
        task['is_good'] = True
        task['title'] = "본 개정안에 찬성합니다."
        task['message'] = "본 개정안의 취지에 깊이 공감하며 적극 찬성합니다."
    return task

if __name__ == "__main__":
    target_date = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not target_date:
        print("\n" + "="*60)
        print(" [자동화 시작] 추출 및 등록을 진행할 마감 날짜를 입력하세요.")
        print(" 형식: YYYY-MM-DD (예: 2026-03-30)")
        print(" 그냥 Enter를 치시면 '최신 전체'를 추출하여 진행합니다.")
        print("="*60)
        user_input = input(" >>> 날짜 입력: ").strip()
        if user_input:
            target_date = user_input

    # 0. 날짜 중복 체크 (백로그 확인)
    history_file = os.path.join(os.path.dirname(__file__), 'processed_bills.json')
    if target_date and os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
                processed_dates = history_data.get('processed_dates', [])
                if target_date in processed_dates:
                    print(f"\n" + "!"*60)
                    print(f" [주의] {target_date}는 이미 처리가 완료된 날짜입니다.")
                    print("!"*60)
                    re_confirm = input(" >>> 그래도 다시 조회하시겠습니까? (y/n): ").strip().lower()
                    if re_confirm != 'y':
                        print("[시스템] 사용자가 취소하여 종료합니다.")
                        sys.exit(0)
        except Exception:
            pass

    # 1. 법안 데이터 자동 추출 및 AI 판별
    tasks = fetch_links.fetch_and_print_links(target_date)
    
    if not tasks:
        print("\n[시스템] 등록할 법안이 없어 프로그램을 종료합니다.")
        sys.exit(0)

    # 2. 사용자 최종 검토 및 개별 수정 단계
    while True:
        print("\n" + "="*60)
        print(" [최종 검토 및 수정] 현재 설정된 찬성/반대 목록입니다.")
        print("-" * 60)
        for i, t in enumerate(tasks):
            status = "✅ [찬성]" if t['is_good'] else "❌ [반대]"
            print(f" {i+1:2d}. {status} {t['bill_title'][:40]}...")
        print("-" * 60)
        print(" 이대로 브라우저를 열고 의견 등록 자동화를 시작하시겠습니까?")
        print(" [진행: y/Enter]  [취소: n]  [상태 뒤집기: e (번호 입력)]")
        print("="*60)
        
        choice = input(" >>> 선택: ").strip().lower()
        
        if choice == 'n':
            exit_confirm = input(" >>> 정말 종료하시겠습니까? 수정하신 내용이 모두 사라집니다. (y/n): ").strip().lower()
            if exit_confirm == 'y':
                print("\n[시스템] 사용자가 실행을 취소하여 프로그램을 종료합니다.")
                sys.exit(0)
            else:
                print(" [시스템] 종료를 취소하고 검토 단계로 돌아갑니다.")
                continue # 다시 리스트로 돌아감
        elif choice == 'e':
            edit_nums = input(" >>> 찬반을 바꿀 법안 번호를 입력하세요 (쉼표로 구분 가능): ").strip()
            try:
                # 쉼표나 공백으로 구분된 번호들 파싱
                indices = [int(n.strip()) - 1 for n in edit_nums.replace(',', ' ').split() if n.strip().isdigit()]
                for idx in indices:
                    if 0 <= idx < len(tasks):
                        tasks[idx] = toggle_bill_status(tasks[idx])
                        print(f" [시스템] {idx+1}번 법안의 상태를 변경했습니다.")
                continue # 리스트 다시 출력
            except Exception as e:
                print(f" [오류] 번호 입력이 잘못되었습니다: {e}")
                continue
        elif choice == 'y' or choice == '':
            break # 반복 종료하고 다음 단계 진행

    # 3. 백로그 업데이트 (중복 처리 방지)
    try:
        processed_ids = []
        processed_dates = []
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
                processed_ids = history_data.get('processed_ids', [])
                processed_dates = history_data.get('processed_dates', [])
        
        current_ids = [t['id'] for t in tasks]
        new_processed_ids = sorted(list(set(processed_ids + current_ids)))
        if target_date and target_date not in processed_dates:
            processed_dates.append(target_date)
        new_processed_dates = sorted(processed_dates)
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump({
                'processed_ids': new_processed_ids, 
                'processed_dates': new_processed_dates,
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=4, ensure_ascii=False)
        print(f"[시스템] {len(current_ids)}개의 법안과 날짜({target_date})를 백로그에 등록했습니다.")
    except Exception as e:
        print(f"[경고] 백로그 업데이트 중 오류 발생: {e}")

    try:
        driver = setup_driver()
        print(f"[시스템] 로그인을 위해 첫 번째 법안 페이지로 이동합니다...")
        driver.get(tasks[0]['url'])
        
        try:
            time.sleep(1)
            driver.switch_to.alert.accept()
        except Exception: pass

        print("\n" + "="*60)
        print(" [중요] 열려있는 창에서 로그인을 완료해 주세요!")
        print(" 로그인이 끝나면 아래 터미널에서 엔터를 치세요!")
        print("="*60 + "\n")
        input(" >>> 로그인을 완료하셨다면 아무 키나 누르고 Enter 키를 치세요: ")

        print(f"\n[시스템] 총 {len(tasks)}개의 법안 세팅을 진행합니다...\n")

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
                
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "txt_sj")))
                except Exception: pass
                
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
                elif "forUpdate.do" in current_url:
                    print(f"[{i+1}/{len(tasks)}] 건너뜀: 이미 의견을 등록한 법안입니다.")
                else:
                    print(f"[{i+1}/{len(tasks)}] 오류: 잘못된 페이지 이동 ({current_url})")
            except Exception as e:
                print(f"[{i+1}/{len(tasks)}] 예외 발생: {e}")

        print("\n" + "="*60)
        print(" [최종 완료] 모든 탭의 세팅이 끝났습니다!")
        print("="*60)
        while True:
            time.sleep(5)
            if not driver.window_handles: break

    except KeyboardInterrupt:
        print("\n[시스템] 종료합니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[시스템 오류] {e}")
