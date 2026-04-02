# Assembly Auto Helper - 개발 진행 현황 및 미해결 이슈

## ⚠️ 미해결 이슈: 보안문자(CAPTCHA) 입력창 자동 포커스 실패

### 현상
- 법안 상세 페이지 진입 후 폼은 정상적으로 채워지나, 보안문자 입력창(`caps_answer`)에 커서가 자동으로 가지 않음.
- 사용자가 매 탭을 클릭할 때마다 수동으로 입력창을 클릭해야 하는 불편함 존재.

### 가설 및 의심 사항
1. **Cross-Origin Iframe**: 보안문자 영역이 메인 도메인과 다른 도메인의 `iframe` 내부에 있을 경우, 브라우저 보안 정책(Same-Origin Policy)으로 인해 외부 스크립트가 내부 요소에 포커스를 줄 수 없음.
2. **Focus Stealing**: 국회 사이트의 자체 스크립트가 로딩 완료 시점에 제목(`txt_sj`)이나 다른 요소로 포커스를 강제로 뺏어감.
3. **Synthetic Event Restriction**: 브라우저(Chrome)가 보안문자 필드에 대한 스크립트 기반의 `focus()` 또는 `click()` 이벤트를 '비정상적 조작'으로 간주하여 무시할 가능성.
4. **Race Condition**: `eager` 로딩 전략 사용 시, DOM은 로드되었으나 보안문자 관련 모듈이 완전히 초기화되지 않은 상태에서 포커스 명령이 수행됨.

### 시도했던 방법들
- **Level 1**: 단순 `setTimeout` 기반 `focus()` 및 `click()` 호출.
- **Level 2**: `window.onfocus` 및 `document.onclick` 이벤트를 가로채서 탭 전환 시마다 포커스 강제.
- **Level 3**: 30초 동안 0.5초 간격으로 `setInterval`을 돌려 끈질기게 포커스 시도.
- **Level 4**: `iframe` 전수 조사 로직 추가 (모든 프레임을 뒤져서 `caps_answer` 탐색).
- **Level 5**: 물리적 클릭 시뮬레이션 (`mousedown`, `mouseup` 이벤트 발생) 및 `tabIndex` 조작.

### 향후 과제
- 실제 브라우저 콘솔에서 `document.getElementById('caps_answer')`가 `null`을 반환하는지, 아니면 존재하지만 포커스만 안 먹는 것인지 확인 필요.
- 보안문자 필드가 `iframe` 내부에 있다면 해당 `iframe`의 `src` 주소를 직접 파악해야 함.
