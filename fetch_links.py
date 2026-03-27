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
    1. 작은 정부 및 자유시장경제 수호: 현재 대한민국 정부는 이미 지나치게 비대해져 있으며, 정부의 권한이 거대해지는 것은 국민의 자유를 억압하고 국가의 효율성을 저해하는 심각한 위협이다. 따라서 정부 조직의 신설, 공공기관의 비대화, 관료주의적 통제권 확대, 그리고 정부가 민간 영역에 개입하려는 모든 시도를 '거대 정부(Big Government)'로 규정하고 강력히 반대한다. 규제 철폐와 감세를 통한 시장 자율성 확대만이 국가의 살길이라고 믿는다.
    2. 철저한 국가 안보 및 제복 입은 영웅 예우: 반공(멸공) 정신을 바탕으로 국가 보안과 국방을 약화시킬 우려가 있는 법안을 강력히 반대한다. 반면, 나라를 위해 헌신하는 군인과 소방관의 처우 개선 및 명예 회복을 위한 법안은 국가 존립의 기초라고 보며 적극 찬성한다.
    3. 외국 자본 공격 방어: 중국 등 외국 자본의 무분별한 국내 부동산 매입, 외국인 참정권 확대 등 주권을 침해하거나 국부를 유출할 여지가 있는 법안에 절대 반대한다.
    4. 선별적 복지 및 포퓰리즘 배격: 무분별한 보편적 복지, 현금 살포 법안을 반대하며 복지는 정말 필요한 사람에게만 제공되는 '선별적 복지'만 지지한다. 특히 더불어민주당 및 그 위성정당들이 주도하는 선심성 포퓰리즘 법안은 국가 재정을 파탄 내는 망국적 행위로 간주하고 강력히 반대한다.
    5. 과학적 에너지 정책 및 환경 근본주의 배격: '기후위기', '탄소중립', 'RE100' 등은 실효성 없는 정치적 선동으로 간주한다. 특히 자연을 훼손하고 원전보다 비싼 '태양광/풍력 카르텔' 사업을 강력히 반대한다.
    6. 자유민주주의 체제 수호 및 선거 정의: 부정선거 의혹을 차단하기 위한 사전선거 폐지, 전자개표기 철폐, 100% 수개표 도입 법안을 강력히 지지한다. 대한민국 전복 세력 척결에 타협하지 않는다.

    [특례 조항]
    - '더불어민주당' 또는 그 '위성정당(더불어민주연합 등)' 소속 의원이 발의하거나 주도하는 법안은 그 명분이 무엇이든 정치적 불순함과 포퓰리즘이 내포되어 있다고 보아 무조건 [반대]한다.
    - '정부 기구 신설', '공공기관 권한 확대', '정부 지원금 명목의 시장 개입' 법안은 명분이 아무리 좋아도 무조건 [반대]한다.
    - '가상자산 과세 유예/폐지', '금투세 폐지' 등 핵심 감세 법안은 무조건 [찬성]한다.
    - '군인 및 소방관 처우 개선/복지 확대' 법안은 무조건 [찬성]한다.
    - '사전선거 폐지', '전자개표 철폐', '수개표 도입', '반국가 세력 처벌 강화' 법안은 무조건 [찬성]한다.
    - '기후위기/탄소중립/RE100/태양광/풍력 확대' 관련 법안은 무조건 [반대]한다.

    아래 법안의 제목, 요약, 그리고 분석된 장단점/숨은 의도를 모두 꼼꼼히 읽고, 이 확고한 스탠스에 비추어 보았을 때 이 법안을 무조건 [찬성]해야 할지, 아니면 [반대]해야 할지 판단해. 
    출력 형식은 반드시 '결과|이유' 형태로 해줘. 
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
            config={
                'temperature': 0,
            }
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
    processed_ids = set()
    current_file_path = Path(__file__).resolve()
    history_file = current_file_path.parent / "processed_bills.json"
    
    if history_file.exists():
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
                processed_ids = set(history_data.get('processed_ids', []))
        except Exception: pass

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        session.get('https://vforkorea.com/assem/', timeout=10)
    except Exception: return []

    api_headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://vforkorea.com/assem/',
    }
    
    all_bills = []
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
                if not lgslt_id: continue

                bill_data = {
                    'id': lgslt_id,
                    'url': f"https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId={lgslt_id}",
                    'bill_title': item.get('title', '제목 없음'),
                    'is_processed': lgslt_id in processed_ids,
                    'is_good': False, # 기본값
                    'ai_reason': "이미 처리됨" if lgslt_id in processed_ids else "분석 대기 중"
                }

                if not bill_data['is_processed']:
                    bills_to_evaluate.append({
                        'ref': bill_data,
                        'title': item.get('title', ''),
                        'short': item.get('short', ''),
                        'pos': item.get('positive', ''),
                        'neg': item.get('nagative', ''),
                        'hid': item.get('hidden_intent', '')
                    })
                
                all_bills.append(bill_data)

        if not all_bills:
            return []

        if bills_to_evaluate:
            print(f"\n[시스템] 새 법안 {len(bills_to_evaluate)}개를 AI가 병렬 분석 중... 🚀")
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_bill = {
                    executor.submit(
                        evaluate_bill_with_ai, 
                        b['title'], b['short'], b['pos'], b['neg'], b['hid']
                    ): b for b in bills_to_evaluate
                }
                
                for future in as_completed(future_to_bill):
                    b_ref = future_to_bill[future]['ref']
                    try:
                        is_good, reason = future.result()
                        b_ref['is_good'] = is_good
                        b_ref['ai_reason'] = reason
                        status_icon = "✅ [찬성]" if is_good else "❌ [반대]"
                        print(f"  {status_icon} {b_ref['bill_title'][:30]}...")
                        print(f"     ㄴ 사유: {reason}")
                    except Exception as e:
                        b_ref['ai_reason'] = f"분석 실패: {e}"

    except Exception as e:
        print(f"[오류 발생] {e}")
        return []

    return all_bills

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if target: fetch_and_print_links(target)
