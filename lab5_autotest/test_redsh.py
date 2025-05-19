
import pytest
import requests
import json
import time


BASE_URL = "https://127.0.0.1:2443/redfish/v1"
USERNAME = "root"
PASSWORD = "0penBmc"
VERIFY_SSL = False  

# Фикстура для создания и закрытия сессии
@pytest.fixture(scope="module")
def auth_session():
    # Создаем новую сессию
    session = requests.Session()
    session.verify = VERIFY_SSL
    session.auth = (USERNAME, PASSWORD)
    
 
    auth_url = f"{BASE_URL}/SessionService/Sessions"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "UserName": USERNAME,
        "Password": PASSWORD
    }
    
    try:
        response = session.post(auth_url, headers=headers, json=payload)
        response.raise_for_status()
        
      
        session.headers.update({
            "X-Auth-Token": response.headers["X-Auth-Token"]
        })
        
        yield session
        
    finally:
    
        if "X-Auth-Token" in session.headers:
            session.delete(f"{auth_url}/{response.json()['Id']}")

def test_authentication(auth_session):
    """Тест аутентификации через Redfish API"""
    print("\n=== Тест аутентификации ===")
    
    # Проверяем, что сессия создана успешно
    assert "X-Auth-Token" in auth_session.headers
    print("✅ Аутентификация прошла успешно")

def test_system_info(auth_session):
    """Тест получения информации о системе"""
    print("\n=== Тест информации о системе ===")
    
    url = f"{BASE_URL}/Systems/system"
    response = auth_session.get(url)
    
   
    assert response.status_code == 200, f"Ожидался код 200, получен {response.status_code}"
    
   
    data = response.json()
    assert "PowerState" in data, "Отсутствует поле PowerState"
    assert "Status" in data, "Отсутствует поле Status"
    
    print(f"✅ Информация о системе получена. Состояние питания: {data['PowerState']}")

def test_power_management(auth_session):
    """Тест управления питанием системы"""
    print("\n=== Тест управления питанием ===")
    
  
    system_url = f"{BASE_URL}/Systems/system"
    response = auth_session.get(system_url)
    initial_state = response.json()["PowerState"]
    print(f"Текущее состояние питания: {initial_state}")
    

    target_action = "On" if initial_state != "On" else "ForceOff"
    action_url = f"{system_url}/Actions/ComputerSystem.Reset"
    

    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "ResetType": target_action
    }
    
    response = auth_session.post(action_url, headers=headers, json=payload)
    
 
    assert response.status_code in [200, 202, 204], \
        f"Ожидался код 200/202/204, получен {response.status_code}"
    
    print(f"✅ Команда {target_action} принята (код {response.status_code}). Ожидаем изменения состояния...")
    
 
    timeout = time.time() + 60
    while time.time() < timeout:
        current_response = auth_session.get(system_url)
        current_state = current_response.json()["PowerState"]
        if current_state != initial_state:
            print(f"Состояние изменилось на: {current_state}")
            break
        time.sleep(5)
    else:
        pytest.fail("Состояние питания не изменилось в течение 60 секунд")
    
 
    if target_action == "ForceOff":
        payload["ResetType"] = "On"
        auth_session.post(action_url, headers=headers, json=payload)

def test_invalid_credentials():
    """Тест аутентификации с неверными учетными данными"""
    print("\n=== Тест неверных учетных данных ===")
    
    url = f"{BASE_URL}/SessionService/Sessions"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "UserName": "invalid_user",
        "Password": "wrong_password"
    }
    
    response = requests.post(url, headers=headers, json=payload, verify=VERIFY_SSL)
    

    assert response.status_code == 401, \
        f"Ожидался код 401, получен {response.status_code}"
    
    print("✅ Неверные учетные данные правильно обработаны")

if __name__ == "__main__":
    pytest.main(["-v", "test_redfish.py"])
#python -m pytest test_redsh.py -v
