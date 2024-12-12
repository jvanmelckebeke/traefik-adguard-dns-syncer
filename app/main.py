import requests
import yaml
from models.adguard import AdguardDomainRewrite, AdguardUpdateDomain
from models.config import Configuration
from models.traefik import Router

def read_config(file_path='/app/config.yaml') -> Configuration:
    """Read and parse the configuration file."""
    with open(file_path, 'r') as f:
        return Configuration(**yaml.safe_load(f))

def get_traefik_domains(server_name: str, ip: str) -> list[str]:
    """Retrieve domains from Traefik routers."""
    print(f"Handling server {server_name} at {ip}")
    response = requests.get(f"http://{ip}:8080/api/http/routers")

    if response.status_code != 200:
        raise Exception(f"Error {response.status_code} getting routers for {server_name}: {response.text}")

    routers = [Router(**raw_router) for raw_router in response.json()]
    return extract_domains(routers)

def extract_domains(routers: list[Router]) -> list[str]:
    """Extract valid domains from Traefik routers."""
    domains = set()
    for router in routers:
        if 'Host(`' in router.rule:
            domain = router.rule.split('Host(`')[1].split('`)')[0]
            if '.' in domain:  # Basic domain validation
                domains.add(domain)
    return sorted(domains)

def get_adguard_rewrites(url: str, username: str, password: str) -> list[AdguardDomainRewrite]:
    """Retrieve AdGuard domain rewrites."""
    response = requests.get(f"{url}/control/rewrite/list", auth=(username, password))

    if response.status_code != 200:
        raise Exception(f"Error {response.status_code} getting rewrites: {response.text}")

    return [AdguardDomainRewrite(**rewrite) for rewrite in response.json()]

def add_adguard_rewrite(url: str, username: str, password: str, rewrite: AdguardDomainRewrite):
    """Add a new AdGuard rewrite rule."""
    response = requests.post(f"{url}/control/rewrite/add", json=rewrite.dict(), auth=(username, password))

    if response.status_code != 200:
        raise Exception(f"Error {response.status_code} adding rewrite: {response.text}")

    print(f"Added rewrite: {rewrite}")

def update_adguard_rewrite(url: str, username: str, password: str, rewrite: AdguardUpdateDomain):
    """Update an existing AdGuard rewrite rule."""
    response = requests.put(f"{url}/control/rewrite/update", json=rewrite.dict(), auth=(username, password))

    if response.status_code != 200:
        raise Exception(f"Error {response.status_code} updating rewrite: {response.text}")

    print(f"Updated rewrite: {rewrite}")

def main():
    """Main function to sync Traefik domains with AdGuard rewrites."""
    print("sync started")
    config = read_config()
    adguard_rewrites = get_adguard_rewrites(config.adguard.address, config.adguard.username, config.adguard.password)

    rewrites_to_add = []
    rewrites_to_update = []

    for server in config.servers:
        all_domains = get_traefik_domains(server.name, server.ip)

        for domain in all_domains:
            matching_rewrite = next((rewrite for rewrite in adguard_rewrites if rewrite.does_resolve(domain)), None)
            if matching_rewrite and matching_rewrite.answer != server.ip:
                rewrites_to_update.append(AdguardUpdateDomain(
                    update=AdguardDomainRewrite(domain=domain, answer=server.ip),
                    target=matching_rewrite
                ))
            elif not matching_rewrite:
                rewrites_to_add.append(AdguardDomainRewrite(domain=domain, answer=server.ip))

    for rewrite in rewrites_to_add:
        add_adguard_rewrite(config.adguard.address, config.adguard.username, config.adguard.password, rewrite)

    for rewrite in rewrites_to_update:
        update_adguard_rewrite(config.adguard.address, config.adguard.username, config.adguard.password, rewrite)

    print("sync complete")

if __name__ == '__main__':
    main()