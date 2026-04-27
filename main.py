import sys
import time
import tempfile
import json
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import fetch_links

def setup_driver():
    options = uc.ChromeOptions()
    temp_dir = tempfile.mkdtemp(prefix="assembly_helper_")
    options.add_argument(f"--user-data-dir={temp_dir}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-search-engine-choice-screen")
    
    # 페이지 로드 전략: 'eager' (DOM만 로드되면 즉시 제어)
    options.page_load_strategy = 'eager'
    
    print("[시스템] 브라우저를 실행합니다...")
    # 현재 설치된 크롬 버전(147)에 맞춰 드라이버 버전 고정
    driver = uc.Chrome(options=options, version_main=147)
    driver.maximize_window()
    return driver

def toggle_bill_status(task):
    if task['is_good']:
        task['is_good'] = False
        task['title'] = "본 개정안에 반대합니다."
        task['message'] = "해당 법안의 문제점이 우려되어 명확히 반대합니다."
    else:
        task['is_good'] = True
        task['title'] = "본 개정안에 찬성합니다."
        task['message'] = "본 개정안의 취지에 깊이 공감하며 적극 찬성합니다."
    return task

def save_backlog(processed_ids_to_add, target_date):
    try:
        history_file = os.path.join(os.path.dirname(__file__), 'processed_bills.json')
        processed_ids = []
        processed_dates = []
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
                processed_ids = history_data.get('processed_ids', [])
                processed_dates = history_data.get('processed_dates', [])
        new_processed_ids = sorted(list(set(processed_ids + processed_ids_to_add)))
        if target_date and target_date not in processed_dates:
            processed_dates.append(target_date)
        new_processed_dates = sorted(processed_dates)
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump({'processed_ids': new_processed_ids, 'processed_dates': new_processed_dates, 'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')}, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[경고] 백로그 업데이트 중 오류 발생: {e}")

if __name__ == "__main__":
    target_date = sys.argv[1] if len(sys.argv) > 1 else None
    if not target_date:
        print("\n" + "="*60)
        print(" [자동화 시작] 마감 날짜를 입력하세요. (YYYY-MM-DD)")
        print("="*60)
        user_input = input(" >>> 날짜 입력: ").strip()
        if user_input: target_date = user_input

    # 1. 모든 법안 데이터 추출
    all_bills = fetch_links.fetch_and_print_links(target_date)
    if not all_bills:
        print("\n[시스템] 법안이 없습니다. 종료합니다.")
        sys.exit(0)

    # 2. 사용자 최종 검토 (전체 현황 보여주기)
    while True:
        unprocessed_tasks = [b for b in all_bills if not b['is_processed']]
        processed_count = len(all_bills) - len(unprocessed_tasks)
        
        print("\n" + "="*60)
        print(f" [전체 현황] {target_date} 마감 법안 (총 {len(all_bills)}개)")
        print(f" (이미 완료: {processed_count}개 / 분석 대기: {len(unprocessed_tasks)}개)")
        print("-" * 60)
        for i, b in enumerate(all_bills):
            if b['is_processed']:
                status = "✔️ [이미 완료]"
            else:
                status = "✅ [분석 찬성]" if b['is_good'] else "❌ [분석 반대]"
            print(f" {i+1:2d}. {status} {b['bill_title'][:40]}...")
        print("-" * 60)
        
        if not unprocessed_tasks:
            print(" [알림] 모든 법안 처리가 완료되었습니다.")
            sys.exit(0)

        print(" 이대로 브라우저를 열고 남은 법안(분석 대기) 자동화를 시작하시겠습니까?")
        print(" [진행: y/Enter]  [취소: n]  [찬반 뒤집기: e (번호 입력)]")
        print("="*60)
        
        choice = input(" >>> 선택: ").strip().lower()
        if choice == 'n':
            if input(" >>> 정말 종료하시겠습니까? (y/n): ").strip().lower() == 'y': sys.exit(0)
            else: continue
        elif choice == 'e':
            edit_nums = input(" >>> 찬반을 바꿀 번호를 입력하세요: ").strip()
            try:
                indices = [int(n.strip()) - 1 for n in edit_nums.replace(',', ' ').split() if n.strip().isdigit()]
                for idx in indices:
                    if 0 <= idx < len(all_bills) and not all_bills[idx]['is_processed']:
                        all_bills[idx] = toggle_bill_status(all_bills[idx])
                continue
            except Exception: continue
        elif choice == 'y' or choice == '':
            tasks = unprocessed_tasks # 실제로 처리할 법안들만 추출
            # 제목/메시지 세팅 (토글됐을 수도 있으므로 여기서 최종 확정)
            for t in tasks:
                if 'title' not in t: # 초기 상태인 경우 세팅
                    t['title'] = "본 개정안에 찬성합니다." if t['is_good'] else "본 개정안에 반대합니다."
                    t['message'] = "본 개정안의 취지에 깊이 공감하며 적극 찬성합니다." if t['is_good'] else "해당 법안의 문제점이 우려되어 명확히 반대합니다."
            break

    try:
        driver = setup_driver()
        driver.get(tasks[0]['url'])
        print("\n" + "="*60)
        print(" [중요] 로그인을 완료한 후, 아래 터미널에서 엔터를 치세요!")
        print("="*60 + "\n")
        input(" >>> 로그인이 끝났다면 Enter 키를 치세요: ")

        print(f"\n[시스템] 남은 {len(tasks)}개의 법안 세팅을 시작합니다...\n")
        processed_ids_successfully = []

        # 배치 단위 처리 (안정성과 속도의 균형)
        BATCH_SIZE = 4
        for i in range(0, len(tasks), BATCH_SIZE):
            batch = tasks[i:i + BATCH_SIZE]
            
            # 1. 배치 단위로 탭 미리 열기
            for j, task in enumerate(batch):
                task_idx = i + j
                try:
                    if task_idx == 0:
                        task['handle'] = driver.window_handles[0]
                        driver.get(task['url'])
                    else:
                        driver.switch_to.new_window('tab')
                        driver.get(task['url'])
                        task['handle'] = driver.current_window_handle
                    
                    # [보완] 탭 생성 직후 즉시 Alert 체크 (다음 탭 생성이 막히는 것 방지)
                    try:
                        alert = driver.switch_to.alert
                        alert_text = alert.text
                        alert.accept()
                        if "이미" in alert_text or "등록" in alert_text:
                            print(f"[{task_idx+1}/{len(tasks)}] 건너뜀: 이미 등록됨 (Alert 확인)")
                            processed_ids_successfully.append(task['id'])
                            task['skip'] = True 
                    except Exception:
                        pass # Alert 없으면 정상

                except Exception as e:
                    # Alert가 떠있어서 생성이 실패한 경우 한 번 더 시도
                    try:
                        alert = driver.switch_to.alert
                        alert.accept()
                        print(f"[{task_idx+1}/{len(tasks)}] 알림 처리 후 재시도...")
                    except:
                        pass
                    print(f"[{task_idx+1}/{len(tasks)}] 탭 생성 실패: {str(e)[:50]}")
                    task['handle'] = None

            # 2. 열린 탭들을 돌며 초고속 폼 채우기
            for j, task in enumerate(batch):
                task_idx = i + j
                if not task.get('handle') or task.get('skip'): continue
                
                try:
                    driver.switch_to.window(task['handle'])
                    
                    # 다시 한 번 Alert 확인 (페이지 로딩 중 뒤늦게 뜨는 경우 대비)
                    try:
                        alert = driver.switch_to.alert
                        alert_text = alert.text
                        alert.accept()
                        if "이미" in alert_text or "등록" in alert_text:
                            if task['id'] not in processed_ids_successfully:
                                processed_ids_successfully.append(task['id'])
                            driver.close()
                            continue
                    except Exception:
                        pass

                    # 'eager' 모드이므로 필수 요소가 나타날 때까지만 대기
                    WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.ID, "txt_sj")))
                    
                    if "forUpdate.do" in driver.current_url:
                        print(f"[{task_idx+1}/{len(tasks)}] 건너뜀: 이미 등록됨 (URL 확인)")
                        processed_ids_successfully.append(task['id'])
                        driver.close() # 이미 등록된 탭은 닫기
                        continue
                    
                    if "forInsert.do" not in driver.current_url:
                        time.sleep(1) # 마지막 확인용 짧은 대기

                    # [최적화] send_keys 대신 JS로 즉시 주입 (비약적으로 빠름)
                    fill_script = """
                        var title = arguments[0];
                        var msg = arguments[1];
                        
                        function fillForm() {
                            var tEl = document.getElementById('txt_sj');
                            var cEl = document.getElementById('txt_cn');
                            if(tEl) { tEl.value = title; tEl.dispatchEvent(new Event('change')); }
                            if(cEl) { cEl.value = msg; cEl.dispatchEvent(new Event('change')); }
                        }
                        
                        function focusCaps() {
                            var caps = document.getElementById('caps_answer') || document.querySelector('input[name="caps_answer"]');
                            if (!caps) {
                                var iframes = document.getElementsByTagName('iframe');
                                for (var i = 0; i < iframes.length; i++) {
                                    try {
                                        var frameDoc = iframes[i].contentDocument || iframes[i].contentWindow.document;
                                        caps = frameDoc.getElementById('caps_answer') || frameDoc.querySelector('input[name="caps_answer"]');
                                        if (caps) break;
                                    } catch(e) {}
                                }
                            }
                            if (caps) {
                                caps.focus();
                                caps.select();
                                caps.style.boxShadow = '0 0 10px red';
                                return true;
                            }
                            return false;
                        }

                        fillForm();
                        focusCaps();
                    """
                    driver.execute_script(fill_script, task['title'], task['message'])

                    print(f"[{task_idx+1}/{len(tasks)}] 완료: {task['bill_title'][:20]}...")
                    processed_ids_successfully.append(task['id'])
                    
                except Exception as e:
                    if "no such window" in str(e).lower():
                        print(f"[{task_idx+1}/{len(tasks)}] 오류: 브라우저 창을 찾을 수 없음")
                    else:
                        print(f"[{task_idx+1}/{len(tasks)}] 폼 작성 중 오류: {str(e)[:50]}")

        if processed_ids_successfully:
            save_backlog(processed_ids_successfully, target_date)
            print(f"\n[시스템] {len(processed_ids_successfully)}개의 법안을 백로그에 기록했습니다.")

        print("\n" + "="*60)
        print(" [최종 완료] 모든 탭의 세팅이 끝났습니다!")
        print(" [안내] 브라우저의 모든 창을 닫으면 프로그램이 자동 종료됩니다.")
        print("="*60)
        
        # 브라우저 감시 루프 강화
        while True:
            try:
                # 창 핸들을 가져오려고 시도 (브라우저가 닫히면 에러 발생)
                handles = driver.window_handles
                if not handles:
                    print("\n[시스템] 모든 창이 닫혀 프로그램을 종료합니다.")
                    break
            except Exception:
                # 브라우저와 연결이 끊긴 경우 (사용자가 강제 종료 등)
                print("\n[시스템] 브라우저 연결이 끊겨 프로그램을 종료합니다.")
                break
            time.sleep(3) # 감시 주기 3초

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"\n[시스템 오류] {e}")
