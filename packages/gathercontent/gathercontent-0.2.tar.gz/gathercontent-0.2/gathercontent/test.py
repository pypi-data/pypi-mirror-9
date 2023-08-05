from client import GatherContent

gc = GatherContent(api_key="82946ce44965046c895898dd1bd693b5a55c90fa0568d02519d7ad0b68fef197", account_name="wearefarm")

print gc.get_page(id=1370975)