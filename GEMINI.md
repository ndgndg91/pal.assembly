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
- **Level 6 (실패)**: **CDP (Chrome DevTools Protocol)**를 활용한 물리적 좌표 클릭(`Input.dispatchMouseEvent`) 및 `DOM.focus` 주입 시도. `getBoundingClientRect()`로 위치를 계산했으나, 여전히 포커스 탈취를 막지 못하거나 좌표 오차로 인해 실패함.

### 향후 과제
- 실제 환경에서 CDP 기반 좌표 클릭이 왜 실패했는지(Iframe 도메인 이슈 등) 정밀 분석 필요.
- 보안문자 영역이 Cross-Origin Iframe인 경우를 대비하여 확장 프로그램(Extension) 기반의 포커스 주입 방식 검토.
- 모든 브라우저 창 종료 시 프로그램이 자동 종료되는 로직(현재 적용됨)의 안정성 모니터링.

