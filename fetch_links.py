import requests
import sys
import re
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from concurrent.futures import ThreadPoolExecutor, as_completed

# .env 파일에서 환경 변수 로드
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if gemini_api_key:
    client = genai.Client(api_key=gemini_api_key)

def evaluate_bill_with_ai(title, short_desc, positive, negative, hidden_intent):
    """
    Gemini AI를 사용하여 법안을 평가하고 이유를 함께 반환합니다.
    """
    if not gemini_api_key:
        return False, "API 키가 없습니다."
        
    prompt = f"""
    너는 대한민국을 사랑하는 보수 우파 성향의 예리한 정치 경제 분석가야. 
    너의 핵심 가치관과 스탠스는 다음과 같아:
    1. 자유시장경제 중시: 불필요한 규제 신설, 세금 인상(가상자산 과세, 금융투자소득세 등), 정부의 시장 개입 확대를 강력히 반대한다. 반대로 세금 감면, 규제 철폐, 시장 자율성 확대 법안은 적극 찬성한다.
    2. 철저한 국가 안보 및 제복 입은 영웅 예우: 반공(멸공) 정신을 바탕으로 국가 보안과 국방을 약화시킬 우려가 있는 법안을 강력히 반대한다. 반면, 나라를 위해 헌신하는 군인과 소방관의 처우 개선, 복지 증진, 명예 회복을 위한 법안은 국가 존립의 기초라고 보며 적극 찬성한다.
    3. 외국 자본 공격 방어: 중국 등 외국 자본의 무분별한 국내 부동산 매입, 외국인 참정권 확대 등 주권을 침해하거나 국부를 유출할 여지가 있는 법안에 절대 반대한다.
    4. 선별적 복지 및 포퓰리즘 배격: 무분별한 보편적 복지, 현금 살포 법안을 반대하며 복지는 정말 필요한 사람에게만 제공되는 '선별적 복지'만 지지한다.
    5. 과학적 에너지 정책 및 환경 근본주의 배격: '기후위기', '탄소중립', 'RE100' 등은 실효성 없는 정치적 선동으로 간주한다. 특히 자연을 훼손하고 원전보다 비싼 '태양광/풍력 카르텔' 사업을 강력히 반대한다.
    6. 자유민주주의 체제 수호 및 선거 정의: 부정선거 의혹을 원천 차단하기 위한 사전선거 폐지, 전자개표기 철폐, 100% 수개표 도입 등 선거의 투명성과 공정성을 확보하는 법안을 강력히 지지한다. 또한 대한민국을 전복하려는 반국가 세력 척결 법안에 타협하지 않는다.

    [특례 조항]
    - '가상자산 과세 유예/폐지', '금투세 폐지' 등 핵심 감세 법안은 무조건 [찬성]한다.
    - '군인 및 소방관 처우 개선/복지 확대' 법안은 무조건 [찬성]한다.
    - '사전선거 폐지', '전자개표 철폐', '수개표 도입', '반국가 세력 처벌 강화' 법안은 무조건 [찬성]한다.
    - '기후위기/탄소중립/RE100/태양광/풍력 확대' 관련 법안은 명분이 아무리 좋아도 무조건 [반대]한다.

    아래 법안의 제목, 요약, 그리고 분석된 장단점/숨은 의도를 모두 꼼꼼히 읽고, 이 확고한 스탠스에 비추어 보았을 때 이 법안을 무조건 [찬성]해야 할지, 아니면 [반대]해야 할지 판단해. 
    출력 형식은 반드시 '결과|이유' 형태로 해줘. (예: 찬성|감세 및 규제 철폐로 시장 활력 증진 기대)
    이유는 한 문장으로 짧고 명확하게 작성해.

    법안 제목: {title}
    법안 요약: {short_desc}
    긍정적 명분: {positive}
    부정적 측면 및 독소조항: {negative}
    숨은 정치적 의도: {hidden_intent}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt,
        )
        raw_result = response.text.strip()
        if "|" in raw_result:
            decision, reason = raw_result.split("|", 1)
        else:
            decision = raw_result
            reason = "사유 미제공"
            
        is_good = "찬성" in decision
        return is_good, reason.strip()
    except Exception as e:
        return False, f"AI 평가 중 오류 발생: {e}"

def fetch_and_print_links(target_date):
    """
    사이트 접속 및 API 호출을 통해 법안 리스트를 가져오고 병렬로 분석합니다.
    """
    # 1. 기존에 처리된 ID 목록 불러오기
    processed_ids = []
    current_file_path = Path(__file__).resolve()
    history_file = current_file_path.parent / "processed_bills.json"
    
    if history_file.exists():
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
                processed_ids = history_data.get('processed_ids', [])
            if processed_ids:
                print(f"[시스템] 백로그에서 {len(processed_ids)}개의 이미 처리된 ID를 불러왔습니다.")
        except Exception:
            pass

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    }
    
    print(f"[시스템] 사이트 접속 및 보안 쿠키 발급 중...")
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        session.get('https://vforkorea.com/assem/', timeout=10)
    except Exception as e:
        print(f"[오류 발생] 메인 페이지 접속 실패: {e}")
        return []

    print(f"[시스템] '{target_date if target_date else '전체'}' 마감 법안 탐색 중...")
    
    api_headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://vforkorea.com/assem/',
    }
    
    bills_to_evaluate = []
    
    try:
        payload = {
            'start': 0, 'size': 500,
            'keyword': target_date if target_date else '',
            'align': '', 'offMyChecked': 0
        }
        
        response = session.post('https://vforkorea.com/api2/assembly/getList.php', headers=api_headers, data=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', [])
            
            for item in items:
                end_date = item.get('end_date', '')
                if target_date and target_date not in end_date:
                    continue
                    
                lgslt_id = item.get('id')
                if lgslt_id and lgslt_id not in processed_ids:
                    bills_to_evaluate.append({
                        'id': lgslt_id,
                        'url': f"https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId={lgslt_id}",
                        'bill_title': item.get('title', '제목 없음'),
                        'short': item.get('short', ''),
                        'positive': item.get('positive', ''),
                        'negative': item.get('nagative', ''),
                        'hidden': item.get('hidden_intent', '')
                    })
        else:
            print(f"[오류 발생] API 응답 코드: {response.status_code}")
            return []

        if not bills_to_evaluate:
            print(f"\n[알림] '{target_date}' 마감인 법안 중 새롭게 처리할 법안이 없습니다.")
            return []

        print(f"\n[시스템] 총 {len(bills_to_evaluate)}개의 법안을 AI가 병렬 분석 중... 🚀")
        
        unique_links = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_bill = {
                executor.submit(
                    evaluate_bill_with_ai, 
                    b['bill_title'], b['short'], b['positive'], b['negative'], b['hidden']
                ): b for b in bills_to_evaluate
            }
            
            for future in as_completed(future_to_bill):
                bill = future_to_bill[future]
                try:
                    is_good_bill, ai_reason = future.result()
                    
                    if is_good_bill:
                        print(f"  ✅ [AI 찬성 판별] {bill['bill_title'][:30]}...")
                        print(f"     ㄴ 사유: {ai_reason}")
                        title, message = "본 개정안에 찬성합니다.", "본 개정안의 취지에 깊이 공감하며 적극 찬성합니다."
                    else:
                        print(f"  ❌ [AI 반대 판별] {bill['bill_title'][:30]}...")
                        print(f"     ㄴ 사유: {ai_reason}")
                        title, message = "본 개정안에 반대합니다.", "해당 법안의 문제점이 우려되어 명확히 반대합니다."
                    
                    unique_links.append({
                        'id': bill['id'], 'url': bill['url'],
                        'title': title, 'message': message, 'bill_title': bill['bill_title']
                    })
                except Exception as e:
                    print(f"  ⚠️ [오류] {bill['bill_title'][:30]} 분석 실패: {e}")

    except Exception as e:
        print(f"[오류 발생] 분석 중 문제 발생: {e}")
        return []

    print(f"\n총 {len(unique_links)}개의 법안에 대한 AI 판별 완료!\n")
    return unique_links

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if target and re.match(r'\d{4}-\d{2}-\d{2}', target):
        fetch_and_print_links(target)
    else:
        print("\n[오류] 날짜 형식이 올바르지 않습니다.")
