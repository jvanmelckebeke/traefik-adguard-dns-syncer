from models.base import BaseSchema


class AdguardDomainRewrite(BaseSchema):
    domain: str
    answer: str

    def does_resolve(self, domain):
        if self.domain == domain:
            return True

        if self.domain.startswith("*."):
            return domain.endswith(self.domain[1:])


class AdguardUpdateDomain(BaseSchema):
    target: AdguardDomainRewrite
    update: AdguardDomainRewrite
