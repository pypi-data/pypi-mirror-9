from utils import installed_modules

def djhcup_components(request):
	return {'djhcup_components': installed_modules()}