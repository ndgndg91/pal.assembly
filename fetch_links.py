import requests
import sys
import re

def fetch_and_print_links(target_date):
    """
    vforkorea.com 의 getList.php API를 호출하여 
    특정 날짜에 마감되는 법안 링크를 추출합니다.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': 'https://vforkorea.com/assem/',
    }
    
    print(f"[시스템] API 서버에서 '{target_date}' 마감 법안 데이터를 가져오는 중...")
    
    unique_links = []
    
    try:
        # 넉넉하게 1~10페이지까지 검색결과를 뒤져서 해당 날짜를 모두 찾습니다.
        for page in range(1, 11):
            payload = {
                'page': page,
                'tab': '',
                'search': target_date,
                'filter': ''
            }
            
            response = requests.post('https://vforkorea.com/api2/assembly/getList.php', data=payload, headers=headers)
            
            if response.status_code != 200:
                break
                
            data = response.json()
            items = data.get('data', [])
            
            if not items:
                break
                
            for item in items:
                # API 응답의 end_date가 우리가 찾는 날짜와 정확히 일치할 때만 수집
                if item.get('end_date') == target_date:
                    lgslt_id = item.get('id')
                    if lgslt_id:
                        url = f"https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaOpn/forInsert.do?menuNo=&refererDiv=S&lgsltPaId={lgslt_id}"
                        if url not in unique_links:
                            unique_links.append(url)
                            
    except Exception as e:
        print(f"[오류 발생] API 통신 중 문제가 생겼습니다: {e}")
        return

    if not unique_links:
        print(f"\n[알림] '{target_date}' 마감인 법안을 찾을 수 없습니다.")
        return

    print(f"\n총 {len(unique_links)}개의 법안을 찾았습니다!\n")
    print("="*100)
    print(" 아래 내용을 복사하여 main.py의 tasks = [ ... ] 안에 붙여넣으세요.")
    print("="*100 + "\n")
    
    for url in unique_links:
        print(f'        {{"url": "{url}", "title": "본 개정안에 반대합니다.", "message": "해당 법안의 문제점이 우려되어 명확히 반대합니다."}},')
        
    print("\n" + "="*100)

if __name__ == "__main__":
    target = None
    
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        print("\n" + "="*60)
        print(" [날짜 입력] 추출을 원하는 마감 날짜를 입력하세요.")
        print(" 형식: YYYY-MM-DD (예: 2026-03-30)")
        print("="*60)
        user_input = input(" >>> 날짜 입력: ").strip()
        if user_input:
            target = user_input
    
    if not target or not re.match(r'\d{4}-\d{2}-\d{2}', target):
        print("\n[오류] 날짜 형식은 YYYY-MM-DD 이어야 합니다. (예: 2026-03-30)")
        sys.exit(1)
        
    fetch_and_print_links(target)
