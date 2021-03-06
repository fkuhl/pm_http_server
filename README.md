# pm_http_server
HTTP server for Peri Meleon. Mediates all access to MongoDB.

## Install
git clone git@github.com:fkuhl/pm_http_server
cd pm_http_server
python3 -m pip install -r requirements.txt

(Note also pm_data_types module must be in PYTHONPATH.)

## Run
python3 ./src/pm_http_server.py

## Household CRUD operations
URL for all Household ops: /api/Households.
Operations are determined by HTTP method and query parameter(s).
Input data is in request body, UTF-8 encoded JSON.
Return status is indicated by HTTP status.
Return data is in response body, UTF-8 encoded, usually JSON.

### Create Household.
- Method: POST.
- Parameters: none.
- Data: new Household (id attr ignored) as JSON.
- Return: stringified Mongo id (not JSON!).

### Read specified Household.
- Method: GET.
- Parameters: id=stringified Mongo id
- Data: none.
- Return: if OK, Household as JSON; else NOTFOUND.

### Read all Households.
- Method: GET.
- Parameters: scope=all|active. (An active Household is one whose head is active.)
- Data: none.
- Return: If OK, array of Households as JSON.

### Update Household.
- Method: PUT.
- Parameters: id=stringified Mongo id.
- Data: Updated Household, including Mongo id, as JSON.
- Return: OK, NOTFOUND, or BAD_REQUEST.

### Delete Household.
- Method: DELETE.
- Parameter: id=stringified Mongo id
- Data: none.
- Return: OK or NOTFOUND.

### Drop Households. (Used for testing.)
- Method: DELETE.
- Parameters: none.
- Data: None.
- Return: OK.

## Member CRUD operations
URL for all Household ops: /api/Members.
Operations are determined by HTTP method and query parameter(s).
Input data is in request body, UTF-8 encoded JSON.
Return status is indicated by HTTP status.
Return data is in response body, UTF-8 encoded, usually JSON.

### Read all Members.
- Method: GET.
- Parameters: scope=all|active.
- Data: none.
- Return: If OK, array of Members as JSON.

### Transaction: move Member.
- URL: /api/Transaction
- Method: PUT.
- Parameters:
    - op='move_member'
    - old_household: stringified Mongo ID of Member's previous household.
    - member_id: id of Member to move
    - new_household: Mongo ID of Household to add Member to.
    - relation='SPOUSE'|'OTHER' whether to add to new Household as spouse or other.
- Data: none.
- Return: OK, NOTFOUND, or BAD_REQUEST.
