import json  # JSON 파일 읽기/쓰기
import os  # 파일 경로 확인 및 화면 지우기
import pickle  # 관리자 비밀번호 직렬화 저장/로드
import re  # 전화번호 숫자 추출 정규식
import sys  # 프로그램 종료
import time  # 출력 대기 시간
# 파일 경로 설정
JSON_FILE_PATH = r".\menu_data.json"  # 메뉴 데이터
STAMP_ACCOUNT = r".\stamp.json"  # 스탬프 데이터
ADMIN_PW_FILE = r".\admin_pw.pkl"  # 관리자 비밀번호
#input에 .strip()을 붙이는 이유: 입력한 문자열이나 숫자의 공백을 제거하기 위해서
# 관리자 모드 관련 함수 (Pickle & 비밀번호)
def save_admin_password(new_pw): #관리자 비밀번호 저장
    dir_path = os.path.dirname(ADMIN_PW_FILE)
    if dir_path and not os.path.exists(dir_path): #해당 경로에 파일이 없으면
        os.makedirs(dir_path, exist_ok=True) #파일을 만든다
    with open(ADMIN_PW_FILE, "wb") as f: #관리자 비밀번호 파일에 pkl 파일로 저장 (열고 > 쓰고)
        pickle.dump(new_pw, f)
def get_admin_password(): #관리자 비밀번호 불러오기
    default_pw = "1234" #초기 비밀번호
    if not os.path.exists(ADMIN_PW_FILE): #해당 관리자비밀번호 파일에 아무것도없으면
        save_admin_password(default_pw) #초기 비밀번호로 관리자 비밀번호 저장
        return default_pw #초기비밀번호값을 리턴한다
    try:
        with open(ADMIN_PW_FILE, "rb") as f: #관리자 비밀번호 파일에 비밀번호가 있으면
            return pickle.load(f) # 비밀번호를 읽어온다
    except Exception: #예외처리 - 이것을 사용하는 이유는 안에 파일이 손상되거나 사라졌다면 관리자 비밀번호 저장함수를 불러와 파일을 만들고 초기비번으로 설정하기 위함
        save_admin_password(default_pw)
        return default_pw
def change_admin_password(): #관리자 비밀번호 변경 로직
    print_header("비밀번호 변경")
    current_pw = get_admin_password()
    input_pw = input("현재 비밀번호를 입력하세요: ").strip()
    if input_pw != current_pw:
        print("\n비밀번호가 일치하지 않습니다.")
        time.sleep(1.5)
        return
    new_pw = input("새로운 비밀번호를 입력하세요: ").strip()
    if not new_pw:
        print("\n빈 비밀번호는 사용할 수 없습니다.")
        time.sleep(1.5)
        return
    confirm_pw = input("새로운 비밀번호 재확인: ").strip()
    if new_pw != confirm_pw:
        print("\n새 비밀번호가 일치하지 않습니다.")
        time.sleep(1.5)
        return
    save_admin_password(new_pw)
    print("\n관리자 비밀번호가 성공적으로 변경되었습니다!")
    time.sleep(1.5)
# 스탬프 관리 함수 (JSON 저장 및 로드)
def load_stamp_data(): #스탬프 정보를 불러오는 함수
    dir_path = os.path.dirname(STAMP_ACCOUNT)
    if dir_path and not os.path.exists(dir_path): #스탬프 정보 파일이 없으면 만든다
        os.makedirs(dir_path, exist_ok=True)
    if not os.path.exists(STAMP_ACCOUNT): #스탬프 정보 파일에 아무것도 없다면
        with open(STAMP_ACCOUNT, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
        return {} #빈 딕셔너리 구조를 넣어준다
    try: #이 예외처리를 하는이유는 json파일은 열어봐야 손상이 되었는지 안되어있는지 알수있기 때문이다!!
        with open(STAMP_ACCOUNT, "r", encoding="utf-8") as f: #손상이 안되었다면 스탬프파일을 읽는다
            return json.load(f) 
    except Exception:
        with open(STAMP_ACCOUNT, "w", encoding="utf-8") as f: #그외 예외처리시 한글이 포함되어 있을 수 있기때문에 한글이 깨지지않게 하는 처리인 ensure_ascii = False를 썻다 
            json.dump({}, f, ensure_ascii=False, indent=4)#indent 는 들여쓰기를 4칸으로 해달라고 하는것.
        return {}
def save_stamp_data(stamp_data): #스탬프내용을 저장하는 함수
    with open(STAMP_ACCOUNT, "w", encoding="utf-8") as f:
        json.dump(stamp_data, f, ensure_ascii=False, indent=4)
def process_stamp_use(cart, total_sum):
    print_header("스탬프 사용 확인")
    print("\n 스탬프를 사용하여 혜택을 받으시겠습니까? (10개 사용 시 혜택 제공)")
    print(" (사용을 원치 않으시면 '0'을 입력하세요.)\n")
    while True:
        phone = input("휴대폰 번호 입력: ").strip()
        if phone == "/exit":
            handle_exit_prompt()
            continue
        if phone == "0":
            print("\n스탬프 사용을 건너뜁니다.")
            time.sleep(1)
            return total_sum, None
        clean_phone = re.sub(r"\D", "", phone) # 폰번호 입력받은걸 숫자로 표현
        if len(clean_phone) == 11 and clean_phone.startswith("010"): #폰번호 길이가 11이고 폰번호 시작이 010 일 경우. 함수설명 :startswith("문자열")은 문자열이 지정된 접두사가 맞는지(맞으면T 틀리면F)
            stamp_db = load_stamp_data()
            current_stamps = stamp_db.get(clean_phone, 0) #스탬프 정보를 불러와 stamp_db에 저장하고 해당 폰번호의 값(스탬프)을 current_stamp에 저장
            masked_phone = f"{clean_phone[:3]}-****-{clean_phone[7:]}" #폰번호 마스크 처리(그냥만들어봄)
            if current_stamps < 10: #스탬프가 10개 미만이면 나오는 처리
                print(f"\n[{masked_phone}] 님의 현재 스탬프는 {current_stamps}개입니다.")
                print(" 스탬프가 10개 이상일 때만 사용이 가능합니다.")
                time.sleep(1.5)
                return total_sum, clean_phone			
            print_header("스탬프 혜택 선택") #스탬프 혜택 선택시
            print(f"\n [{masked_phone}] 님 (보유 스탬프: {current_stamps}개)")
            print(" 사용 가능한 혜택을 선택해 주세요 (스탬프 10개 차감):\n")
            print(" 1. 2,000원 할인 받기\n 2. 아메리카노 1잔 무료 받기\n 0. 사용 안함")
            print("-" * 90)
            while True:
                choice = input("선택 (1/2/0): ").strip()
                if choice == "1":
                    discount = 2000
                    total_sum = max(0, total_sum - discount) #2000원 할인계산
                    stamp_db[clean_phone] -= 10 #스탬프 차감
                    save_stamp_data(stamp_db) #저장
                    print("\n 2,000원 할인이 적용되었습니다!")
                    print(f" 남은 스탬프: {stamp_db[clean_phone]}개 (10개 차감됨)")
                    time.sleep(1.5)
                    return total_sum, clean_phone
                elif choice == "2": #아메리카노 증정
                    print("아메리카노 옵션을 선택하세요. 1. HOT 2.ICE")
                    AME_choice = input("선택: ").strip()
                    if AME_choice == "1": 
                     free_item = {
                        "name": "[스탬프 증정] 아메리카노",
                        "unit_price": 0,
                        "final_price": 0,
                        "quantity": 1,
                        "options": ["HOT", "기본 샷"],
                        "category_id": "cat_coffee",
                     }
                     cart.append(free_item)
                     stamp_db[clean_phone] -= 10
                     save_stamp_data(stamp_db)
                     print(
                        "\n [스탬프 증정] 아메리카노(HOT) 1잔이 추가되었습니다!"
                     )
                     print(
                         f" 남은 스탬프: {stamp_db[clean_phone]}개 (10개 차감됨)"
                     )
                     time.sleep(1.5)
                     return total_sum, clean_phone
                    if AME_choice == "2": 
                     free_item = {
                        "name": "[스탬프 증정] 아메리카노",
                        "unit_price": 0,
                        "final_price": 0,
                        "quantity": 1,
                        "options": ["ICE", "기본 샷"],
                        "category_id": "cat_coffee",
                     }
                     cart.append(free_item)
                     stamp_db[clean_phone] -= 10
                     save_stamp_data(stamp_db)
                     print(
                        "\n [스탬프 증정] 아메리카노(ICE) 1잔이 추가되었습니다!"
                     )
                     print(
                         f" 남은 스탬프: {stamp_db[clean_phone]}개 (10개 차감됨)"
                     )
                     time.sleep(1.5)
                     return total_sum, clean_phone
                elif choice == "0":
                    print("\n스탬프 사용을 취소합니다.")
                    time.sleep(1)
                    return total_sum, clean_phone
                else:
                    print("올바른 번호를 선택해 주세요.")
        else:
          print("\n올바른 휴대폰 번호 형식이 아닙니다. (예: 01012345678)")
def process_stamp_earn(earned_count, used_phone=None): # 스탬프 적립 로직 earnde_count 이건 음료갯수를 뜻함
    if earned_count <= 0:
        print("\n 적립 가능한 음료 항목이 없어 스탬프 적립을 건너뜁니다.")
        time.sleep(1.5)
        return used_phone
    print_header("스탬프 적립")
    print(f"\n 이번 주문으로 적립 가능한 스탬프: {earned_count}개")
    print(" (디저트 메뉴는 스탬프 적립 대상에서 제외됩니다.)")
    print(" 핸드폰 번호를 '-' 없이 숫자만 입력해 주세요. (예: 01012345678)")
    if used_phone:
        masked_used = f"{used_phone[:3]}-****-{used_phone[7:]}"
        print(f" ▶ 이전 입력된 번호 [{masked_used}]로 자동 적립하시려면 [Enter]를 누르세요.")
    print(" (적립을 원하지 않으시면 '0'을 입력하세요.)\n")
    while True:
        phone = input("휴대폰 번호 입력: ").strip()
        if phone == "" and used_phone:
            clean_phone = used_phone
        elif phone == "/exit":
            handle_exit_prompt()
            continue
        elif phone == "0":
            print("\n스탬프 적립을 건너뜁니다.")
            time.sleep(1)
            return None
        else:
            clean_phone = re.sub(r"\D", "", phone)
        if len(clean_phone) == 11 and clean_phone.startswith("010"):
            stamp_db = load_stamp_data()
            current_stamps = stamp_db.get(clean_phone, 0)
            total_stamps = current_stamps + earned_count
            stamp_db[clean_phone] = total_stamps
            save_stamp_data(stamp_db)
            masked_phone = f"{clean_phone[:3]}-****-{clean_phone[7:]}"
            print(f"\n[{masked_phone}] 님께 스탬프 {earned_count}개가 적립되었습니다!")
            print(f" 보유 스탬프: {current_stamps}개 ➔ 총 {total_stamps}개")
            time.sleep(2)
            return masked_phone
        else:
            print("\n올바른 휴대폰 번호 형식이 아닙니다. (예: 01012345678)")
# 관리자 모드 관련 기능
def save_kiosk_data(file_path, data): #메뉴관련 저장함수
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
def admin_add_menu(data):#메뉴추가
    print_header("메뉴 추가")
    categories = data["categories"]
    print("카테고리 목록:")
    for idx, cat in enumerate(categories, 1): #enumerate()를 쓴 이유: 인덱스는 0부터 시작해서 이거없이 출력하면 0 어쩌고 1 어쩌고 로 나오기때문에 1부터 표시하라고 썼음
        print(f"   {idx}. {cat['category_name']}") 
    print("-" * 90)
    cat_choice = input("메뉴를 추가할 카테고리 번호를 선택하세요: ").strip()
    if not cat_choice.isdigit() or not (1 <= int(cat_choice) <= len(categories)):
        print("\n 올바른 카테고리 번호가 아닙니다.")
        time.sleep(1.5)
        return
    target_category = categories[int(cat_choice) - 1]
    name = input("새 메뉴 이름: ").strip()
    if not name:
        print("\n 메뉴 이름을 입력해야 합니다.")
        time.sleep(1.5)
        return
    price_str = input("메뉴 가격(숫자): ").strip()
    if not price_str.isdigit():
        print("\n 가격은 숫자만 입력해야 합니다.")
        time.sleep(1.5)
        return
    price = int(price_str)
    item_id = f"custom_{int(time.time())}"
    print("\n사용 가능한 옵션 그룹 목록:")
    opt_groups = data.get("option_groups", [])
    for idx, og in enumerate(opt_groups, 1):
        print(f"   {idx}. {og['group_name']} ({og['group_id']})")
    selected_opts = input("적용할 옵션 번호들을 쉼표(,)로 구분해 입력하세요 (예: 1,2,5 / 없으면 Enter): ").strip()
    avail_groups = []
    if selected_opts:
        indices = []
        for s in selected_opts.split(","):
            clean_s = s.strip()
            if clean_s.strip().isdigit():
                indices.append(clean_s)
        for i in indices:
            idx = int(i)
            if 1 <= idx <= len(opt_groups):
                avail_groups.append(opt_groups[idx - 1]["group_id"])
    new_item = {
        "id": item_id,
        "name": name,
        "price": price,
        "available_option_groups": avail_groups,
        "sold_out": False,
    }
    target_category["items"].append(new_item)
    save_kiosk_data(JSON_FILE_PATH, data)
    print(f"\n[{name}] 메뉴가 추가되었습니다!")
    time.sleep(1.5)
def admin_delete_menu(data): #메뉴삭제 함수
    print_header("메뉴 삭제")
    categories = data["categories"]
    for idx, cat in enumerate(categories, 1):
        print(f"   {idx}. {cat['category_name']}")
    print("-" * 90)
    cat_choice = input("삭제할 메뉴가 있는 카테고리 번호: ").strip()
    if not cat_choice.isdigit() or not (1 <= int(cat_choice) <= len(categories)):
        print("\n올바른 카테고리 번호가 아닙니다.")
        time.sleep(1.5)
        return
    target_category = categories[int(cat_choice) - 1]
    items = target_category["items"]
    if not items:
        print("\n해당 카테고리에 등록된 메뉴가 없습니다.")
        time.sleep(1.5)
        return
    print("\n[메뉴 목록]")
    for i, item in enumerate(items, 1):
        if item.get("sold_out", False):
            status = "[품절]"
        else:
            status = "[판매중]"
        print(f"   {i}. {item['name']} - {item['price']:,}원 {status}")
    print("-" * 90)
    item_idx_str = input("삭제할 메뉴 번호: ").strip()
    if item_idx_str.isdigit() and 1 <= int(item_idx_str) <= len(items):
        del_item = items.pop(int(item_idx_str) - 1)
        save_kiosk_data(JSON_FILE_PATH, data)
        print(f"\n[{del_item['name']}] 메뉴가 삭제되었습니다.")
    else:
        print("\n 올바른 메뉴 번호가 아닙니다.")
    time.sleep(1.5)
def admin_toggle_sold_out(data):# 품절상태 관리 함수
    while True:
        print_header("품절 상태 관리 및 조회")
        categories = data["categories"]
        print(" [현재 품절된 메뉴 목록]")
        sold_out_count = 0
        for cat in categories:
            for item in cat["items"]:
                if item.get("sold_out", False):
                    print(f"   - [{cat['category_name']}] {item['name']}")
                    sold_out_count += 1
        if sold_out_count == 0:
            print("   (현재 품절된 메뉴가 없습니다.)")
        print("\n" + "=" * 90)
        print(" 1. 품절 / 판매중 상태 전환")
        print(" 0. 관리자 메인으로 돌아가기")
        print("=" * 90)
        choice = input("선택: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            print(f"\n카테고리 번호를 선택하세요 (1~{len(categories)}):")
            for idx, cat in enumerate(categories, 1):
                print(f"   {idx}. {cat['category_name']}")
            cat_choice = input("선택: ").strip()
            if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
                target_category = categories[int(cat_choice) - 1]
                items = target_category["items"]
                if not items:
                    print("\n해당 카테고리에 메뉴가 없습니다.")
                    time.sleep(1.5)
                    continue
                print("\n[메뉴 목록]")
                for i, item in enumerate(items, 1):
                    if item.get("sold_out", False):
                        status = "[품절]"
                    else:
                        status = "[판매중]"
                    print(f"   {i}. {item['name']} - {status}")
                m_idx_str = input("\n상태를 변경할 메뉴 번호: ").strip()
                if (m_idx_str.isdigit()and 1 <= int(m_idx_str) <= len(items)):
                    target_item = items[int(m_idx_str) - 1]
                    current_status = target_item.get("sold_out", False)
                    target_item["sold_out"] = not current_status
                    save_kiosk_data(JSON_FILE_PATH, data)
                    if target_item["sold_out"]:
                        new_status_str = "품절"
                    else:
                        new_status_str = "판매중"
                    print(f"\n[{target_item['name']}] 메뉴 상태가 [{new_status_str}](으)로 변경되었습니다.")
                    time.sleep(1.5)
            else:
                print("\n 잘못 선택하셨습니다.")
                time.sleep(1.5)
def run_admin_mode(data): #관리자 모드
    current_pw = get_admin_password()
    print_header("관리자 인증")
    pw_input = input("관리자 비밀번호를 입력하세요: ").strip()
    if pw_input != current_pw:
        print("\n비밀번호가 올바르지 않습니다.")
        time.sleep(1.5)
        return
    while True:
        print_header("관리자 모드")
        print("   1. 메뉴 추가")
        print("   2. 메뉴 삭제")
        print("   3. 품절 메뉴 관리 및 조회")
        print("   4. 관리자 비밀번호 변경")
        print("   5. 키오스크 프로그램 전체 종료")
        print("   0. 키오스크 화면으로 돌아가기")
        print("-" * 90)
        choice = input("선택하세요: ").strip()
        if choice == "1":
            admin_add_menu(data)
        elif choice == "2":
            admin_delete_menu(data)
        elif choice == "3":
            admin_toggle_sold_out(data)
        elif choice == "4":
            change_admin_password()
        elif choice == "5":
            print("\n" + "!" * 50)
            confirm = (input("정말로 키오스크 프로그램을 종료하시겠습니까? (Y/N): ").strip())
            print("!" * 50)
            if confirm in ["Y", "y", "ㅛ", "ㅇ"]:
                print("\n키오스크 프로그램을 종료합니다. 이용해 주셔서 감사합니다!")
                sys.exit(0)
            else:
                print("\n프로그램 종료를 취소합니다.")
                time.sleep(1)
        elif choice == "0":
            print("\n관리자 모드를 종료합니다...")
            time.sleep(1)
            break
        else:
            print("\n잘못된 입력입니다.")
            time.sleep(1)
# 키오스크 메인 로직
def load_kiosk_data(file_path): #키오스크 정보 로드
    if not os.path.exists(file_path):
        print(f"오류: '{file_path}' 파일을 찾을 수 없습니다.")
        print("스크립트와 같은 경로에 'menu_data.json' 파일이 있는지 확인해 주세요.")
        sys.exit(1)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        print(f"오류: '{file_path}' 파일의 형식이 올바르지 않은 JSON 데이터입니다.")
        sys.exit(1)
def clear_screen(): #화면이 바낄때마다 청소해주는거
    if os.name == "nt": 
        os.system("cls")
    else:
        os.system("clear")
def print_header(title="BULK COFFEE KIOSK"):
    clear_screen()
    print(f"{title:^90}")
def handle_exit_prompt():
    print("\n" + "!" * 50)
    print("키오스크 종료는 관리자 모드(/admin)에서만 가능합니다.")
    print("!" * 50)
    time.sleep(1.5)
def select_dining_type(data):
    while True:
        print_header("BULK COFFEE KIOSK")
        print("=" * 90)
        print("\n   안녕하세요! 벌크커피입니다.")
        print("   원하시는 이용 방식을 선택해 주세요.\n")
        print("   1. 먹고 가기")
        print("   2. 포장 하기")
        print("-" * 90)
        choice = input("선택하세요: ").strip()
        if choice == "/exit":
            handle_exit_prompt()
            continue
        elif choice == "/admin":
            run_admin_mode(data)
            continue
        elif choice == "1":
            return "매장 이용"
        elif choice == "2":
            return "포장하기"
        else:
            print("\n잘못 입력하셨습니다. 1번 또는 2번을 입력해 주세요.")
            time.sleep(1)
def customize_item_options(item, option_groups_map):
#메뉴 옵션 선택 처리 ("max_selectable" 키가 있는 그룹은 옵션 선택 후 수량을 숫자로 입력해 그 값까지 담을 수 있음)
    selected_options_desc = []
    additional_price = 0
    avail_groups = item.get("available_option_groups", [])
    if not avail_groups:
        return selected_options_desc, additional_price
    for grp_id in avail_groups:
        grp = option_groups_map.get(grp_id)
        if not grp:
            continue
        grp_name = grp["group_name"]
        is_required = grp.get("required", False)
        options = grp["options"]
        max_selectable = grp.get("max_selectable", 1)  # max_selectable 키가 없으면 기본값 1개
        if is_required:
            req_str = " (필수)"
        else:
            req_str = " (선택)"
        remaining = max_selectable  # 이 옵션 그룹에서 더 담을 수 있는 남은 개수
        while remaining > 0:
            print(f"\n▶ [{grp_name}]" + req_str)
            if max_selectable > 1:
                picked = max_selectable - remaining
                print(f"    (최대 {max_selectable}개까지 선택 가능 / 현재 {picked}개 선택됨 / 남은 개수 {remaining}개)")
            for idx, opt in enumerate(options, 1):
                price = opt.get("price", 0)
                if price > 0:
                    price_str = f" (+{price:,}원)"
                else:
                    price_str = ""
                print(f"    {idx}. {opt['name']}{price_str}")
            # 필수 옵션인데 아직 하나도 선택하지 않았다면 넘어갈수없음
            can_stop = (not is_required) or remaining < max_selectable
            if can_stop:
                if remaining < max_selectable:
                    print("    0. 선택 완료 (더 담지 않음)")
                else:
                    print("    0. 선택 안 함")
            if can_stop:
                prompt = f"선택하세요 (1~{len(options)}, 0: 종료): "
            else:
                prompt = f"선택하세요 (1~{len(options)}): "
            choice = input(prompt).strip()
            if choice == "0":
                if can_stop:
                    break
                print("최소 1개는 선택해야 합니다.")
                continue
            if not (choice.isdigit() and 1 <= int(choice) <= len(options)):
                print("올바른 번호를 선택해 주세요.")
                continue
            selected_opt = options[int(choice) - 1]
            # 최대 선택 개수가 1보다 크면, 중복 선택 대신 수량을 숫자로 입력받는다
            if max_selectable > 1 and remaining > 1:
                while True:
                    qty_str = input(
                        f"'{selected_opt['name']}' 몇 개를 추가하시겠습니까? (1~{remaining}, 기본 1): "
                    ).strip()
                    if not qty_str:
                        qty = 1
                        break
                    if qty_str.isdigit() and 1 <= int(qty_str) <= remaining:
                        qty = int(qty_str)
                        break
                    print(f"1~{remaining} 사이의 숫자를 입력해 주세요.")
            else:
                qty = 1
            desc = selected_opt["name"] if qty == 1 else f"{selected_opt['name']} x{qty}"
            selected_options_desc.append(desc)
            additional_price += selected_opt.get("price", 0) * qty
            remaining -= qty
            if remaining <= 0:
                time.sleep(0.8)
    return selected_options_desc, additional_price
def process_receipt_print(cart, dining_type, stamp_phone, total_sum, order_number, earned_stamp_count):
    print_header(" 영수증 발행 여부")
    print("=" * 90)
    print("\n 영수증을 출력하시겠습니까?\n")
    print("   - 출력   : 영수증을 출력합니다.")
    print("   - 안함   : 영수증을 출력하지 않습니다.\n")
    print("-" * 90)
    while True:
        receipt_choice = input("입력 (출력 / 안함): ").strip()
        if receipt_choice == "/exit":
            handle_exit_prompt()
            continue
        if receipt_choice == "출력":
            print_header("주문 영수증")
            print("=" * 42 + "영수증" + "=" * 42)
            print(f"이용 구분: {dining_type}")
            if stamp_phone:
                print(f"스탬프 적립: {stamp_phone} (이번 적립: {earned_stamp_count}개)")
            else:
                print("스탬프 적립: 미적립")
            print("-" * 90)
            for order in cart:
                if order["quantity"] > 1:
                    qty_str = f" x{order['quantity']}"
                else:
                    qty_str = ""
                if order["options"]:
                    opts_str = f" ({', '.join(order['options'])})"
                else:
                    opts_str = ""
                print(f"- {order['name']}{qty_str}{opts_str}")
                print(f"   금액: {order['final_price']:,}원")
            print("-" * 90)
            print(f"합계 금액: {total_sum:,}원")
            print("=" * 90)
            print(f"주문 번호 [ {order_number}번 ] 완료. 이용해주셔서 감사합니다!\n")
            input("초기 화면으로 돌아가려면 [Enter] 키를 누르세요...")
            break
        elif receipt_choice == "안함":
            print_header("주문 완료")
            print("=" * 90)
            print("\n 영수증을 출력하지 않습니다.")
            print(f" 주문 번호 [ {order_number}번 ] 완료. 이용해주셔서 감사합니다!\n")
            time.sleep(2)
            break
        else:
            print("\n'출력' 또는 '안함'을 정확히 입력해 주세요.")
def process_cart_view_and_checkout(cart, dining_type, order_counter):
    #장바구니 확인, 초기화, 결제 진행 처리 함수
    print_header("장바구니 확인 및 결제")
    print("=" * 90)
    if not cart:
        print("\n 현재 장바구니가 비어 있습니다.")
        input("\n메뉴 화면으로 돌아가려면 [Enter] 키를 누르세요...")
        return order_counter, False
    total = sum(c["final_price"] for c in cart)
    print(" [담긴 메뉴 목록]\n")
    for idx, c_item in enumerate(cart, 1):
        if c_item["options"]:
            opts = f" ({', '.join(c_item['options'])})"
        else:
            opts = ""
        print(f"   {idx}. {c_item['name']}{opts} x{c_item['quantity']} - {c_item['final_price']:,}원")
    print("-" * 90)
    print(f" 총 결제 예정 금액: {total:,}원")
    print("-" * 90)
    print(" [P] 결제하기  |  [R] 장바구니 비우기  |  [C] 계속 쇼핑하기")
    print("-" * 90)
    while True:
        action = input("선택하세요 (P/R/C): ").strip().upper()
        if action == "C":
            return order_counter, False
        elif action == "R":
            cart.clear()
            print("\n 장바구니를 완전히 비웠습니다.")
            time.sleep(1.5)
            return order_counter, False
        elif action == "P":
            total_sum = sum(item["final_price"] for item in cart)
            # 1. 스탬프 사용
            total_sum, used_phone = process_stamp_use(cart, total_sum)
            # 2. 결제 진행
            print_header("결제 진행")
            print("=" * 90)
            print(f"\n 총 결제 금액: {total_sum:,}원")
            print(" IC 카드를 투입구에 넣고 결제를 완료해 주세요...")
            time.sleep(2)
            # 3. 스탬프 적립
            earned_stamp_count = sum(
                item["quantity"]
                for item in cart
                if item.get("category_id") != "cat_dessert"
                and "[스탬프 증정]" not in item["name"]
            )
            stamp_phone = process_stamp_earn(earned_stamp_count, used_phone)
            # 4. 영수증 출력
            process_receipt_print(
                cart,
                dining_type,
                stamp_phone,
                total_sum,
                order_counter,
                earned_stamp_count,
            )
            return order_counter + 1, True
        else:
            print("올바른 명령어를 입력해 주세요. (P: 결제 / R: 비우기 / C: 계속 쇼핑)")
def select_menu_from_category(selected_cat, option_groups_map, cart):
    # 선택한 카테고리 내부에서 메뉴를 선택하는 단계
    items = selected_cat["items"]
    while True:
        print_header(f"[{selected_cat['category_name']}] 메뉴 선택")
        print("=" * 90)
        if not items:
            print("\n   (해당 카테고리에 등록된 메뉴가 없습니다.)")
        else:
            print(" [메뉴 목록]\n")
            for idx, item in enumerate(items, 1):
                if item.get("sold_out", False):
                    status = " [품절]"
                else:
                    status = ""
                print(f"   {idx}. {item['name']} - {item['price']:,}원{status}")
        cart_count = sum(c["quantity"] for c in cart)
        total_price = sum(c["final_price"] for c in cart)
        print("\n" + "-" * 90)
        print(f" 장바구니: 총 {cart_count}개 선택됨 ({total_price:,}원)")
        print("-" * 90)
        print(" [0] 메인 화면(카테고리 탭)으로 돌아가기")
        print("-" * 90)
        choice = input("구매할 메뉴 번호를 입력하세요: ").strip()
        if choice == "0":
            break
        if choice.isdigit():
            m_idx = int(choice)
            if 1 <= m_idx <= len(items):
                selected_item = items[m_idx - 1]
                if selected_item.get("sold_out", False):
                    print("\n 죄송합니다. 해당 메뉴는 현재 품절입니다.")
                    time.sleep(1.5)
                    continue
                print_header(f" [옵션 선택] {selected_item['name']}")
                print("=" * 90)
                opt_descs, add_price = customize_item_options(selected_item, option_groups_map)
                print_header(f" [수량 선택] {selected_item['name']}")
                print("=" * 90)
                while True:
                    qty_str = input("\n수량을 입력하세요 (기본 1): ").strip()
                    if not qty_str:
                        quantity = 1
                        break
                    if qty_str.isdigit() and int(qty_str) > 0:
                        quantity = int(qty_str)
                        break
                    print("올바른 수량을 숫자(1 이상)로 입력해주세요.")
                unit_price = selected_item["price"] + add_price
                # 동일 메뉴 + 동일 옵션 중복 체크 로직
                found = False
                for cart_item in cart:
                    # 메뉴 이름과 선택한 옵션 리스트가 완벽히 일치하는지 확인
                    if (cart_item["name"] == selected_item["name"]
                        and cart_item["options"] == opt_descs
                        and cart_item["category_id"] == selected_cat["category_id"]):
                        # 기존 항목의 수량 증가 및 최종 가격 재계산
                        cart_item["quantity"] += quantity
                        cart_item["final_price"] = cart_item["unit_price"] * cart_item["quantity"]
                        found = True
                        break
                # 기존 장바구니에 없는 새로운 항목(또는 옵션이 다른 경우) 추가
                if not found:
                    final_price = unit_price * quantity
                    cart.append(
                        {
                            "name": selected_item["name"],
                            "unit_price": unit_price,
                            "final_price": final_price,
                            "quantity": quantity,
                            "options": opt_descs,
                            "category_id": selected_cat["category_id"],
                        }
                    )
                print(f"\n [{selected_item['name']}] {quantity}개가 장바구니에 추가되었습니다!")
                time.sleep(1)
                break
            else:
                print("\n올바른 메뉴 번호를 입력해 주세요.")
                time.sleep(1)
        else:
            print("\n숫자로 번호를 입력해 주세요.")
            time.sleep(1)
def main(): #메인 로직
    order_counter = 1
    while True:
        kiosk_data = load_kiosk_data(JSON_FILE_PATH) #키오스크 데이터 불러오기
        categories = kiosk_data.get("categories", []) #카데고리 불러오기
        option_groups = kiosk_data.get("option_groups", []) #옵션그룹 불러오기
        option_groups_map = {} #옵션 그룹내의 옵션들 불러오기 
        for og in option_groups:
            key = og["group_id"]
            option_groups_map[key] = og
        dining_type = select_dining_type(kiosk_data)
        cart = [] #카데고리 페이징 관련 변수
        cat_page = 0
        cats_per_page = 5  # 한 화면에 표시할 카테고리 탭 수
        # 메인 화면 (카테고리 탭 상단 표시)
        while True:
            print_header(f"BULK COFFEE KIOSK - 메인 화면 ({dining_type})")
            print("=" * 90)
            total_cats = len(categories)
            max_page = ((total_cats - 1) // cats_per_page if total_cats > 0 else 0)
            # 현재 페이지의 카테고리 슬라이싱
            start_idx = cat_page * cats_per_page
            end_idx = min(start_idx + cats_per_page, total_cats)
            page_cats = categories[start_idx:end_idx]
            # 상단 탭 텍스트 구성
            tab_parts = []
            for idx, cat in enumerate(page_cats, start_idx + 1):
                tab_parts.append(f"{idx}.{cat['category_name']}")
            tab_str = " | ".join(tab_parts)
            # 페이징 컨트롤 버튼 구성
            display_parts = []
            if cat_page > 0:
                display_parts.append("[< 이전]")
            display_parts.append(tab_str)
            if cat_page < max_page:
                display_parts.append("[다음 >]")
            display_tabs = "  ".join(display_parts)
            print(display_tabs)
            print("=" * 90)
            print("\n 상단 탭에서 원하시는 카테고리 번호를 선택해주세요.")
            if max_page > 0:
                print(" - '>' 입력: 다음 카테고리 페이지로 이동")
                print(" - '<' 입력: 이전 카테고리 페이지로 이동")
            cart_count = sum(c["quantity"] for c in cart)
            total_price = sum(c["final_price"] for c in cart)
            print("\n" + "-" * 90)
            print(f" 장바구니 : 총 {cart_count}개 선택됨 ({total_price:,}원)")
            print("-" * 90)
            user_input = (input(" 카데고리번호  |  [I] 장바구니  |  [>, <] 이동  :").strip().upper())
            if user_input == "/ADMIN":
                run_admin_mode(kiosk_data)
                break
            elif user_input == "/EXIT":
                handle_exit_prompt()
                continue
            elif user_input in [">", "."] and cat_page < max_page:
                cat_page += 1
                continue
            elif user_input in ["<", ","] and cat_page > 0:
                cat_page -= 1
                continue
            elif user_input == "I":
                order_counter, is_completed = process_cart_view_and_checkout(cart, dining_type, order_counter)
                if is_completed:
                    break
                else:
                    continue
            # 카테고리 번호 선택 시
            if user_input.isdigit():
                cat_num = int(user_input)
                if 1 <= cat_num <= total_cats:
                    selected_cat = categories[cat_num - 1]
                    select_menu_from_category(selected_cat, option_groups_map, cart)
                else:
                    print("\n 올바른 카테고리 번호가 아닙니다.")
                    time.sleep(1)
            else:
                print("\n 올바른 번호나 명령어를 입력해 주세요.")
                time.sleep(1)
main()