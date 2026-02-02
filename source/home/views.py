from django.views.generic import TemplateView
from .models import HomePage, TermsAndPolicies
from django.http import Http404


class HomePageView(TemplateView):
    """
    Renders the home page with featured and best-selling products,
    homepage content, and pricing settings.
    """
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "home": HomePage.objects.first(),
            }
        )

        return context


class PolicyPageView(TemplateView):
    """
    Renders any policy page based on policy_type in the URL.
    """
    template_name = "policy_page.html"  # generic template

    POLICY_FIELDS = {
        "terms-of-service": "terms_of_service",
        "privacy-policy": "privacy_policy",
        "refund-policy": "refund_policy",
        "shipping-policy": "shipping_policy",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        policy_type = self.kwargs.get("policy_type")
        if policy_type not in self.POLICY_FIELDS:
            raise Http404("Policy not found")

        policies = TermsAndPolicies.objects.first()
        if not policies:
            raise Http404("Policies not configured")

        field_name = self.POLICY_FIELDS[policy_type]
        context["policy_title"] = policy_type.replace("-", " ").title()
        context["policy_content"] = getattr(policies, field_name)
        return context
