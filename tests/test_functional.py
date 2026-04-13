import pytest
from src.manager import Manager
from src.models import Parameters

def test_czy_suma_sie_zgadza_z_mieszkania():
    manager = Manager(Parameters())
    apartment_key = 'apart-polanka'
    year = 2025
    month = 1
    apartment_settlement = manager.get_settlement(apartment_key, year, month)
    assert apartment_settlement is not None, "Rozliczenie dla mieszkania powinno zostać wygenerowane."

    tenant_settlements = manager.create_tenants_settlements(apartment_settlement)
    assert tenant_settlements is not None, "Rozliczenia dla lokatorów powinny zostać wygenerowane."
    assert len(tenant_settlements) > 0, "W mieszkaniu powinni być przypisani jacyś lokatorzy."
    total_tenants_due = sum(ts.total_due_pln for ts in tenant_settlements)

    assert total_tenants_due == pytest.approx(apartment_settlement.total_due_pln), \
        f"Suma obciążeń lokatorów ({total_tenants_due}) nie zgadza się z kosztem mieszkania ({apartment_settlement.total_due_pln})"
    
def test_dluznicy():
        manager = Manager(Parameters())
        debtors = manager.dluznicy(year=2025, month=1)
        assert isinstance(debtors, list), "Metoda powinna zwracać listę dłużników."
        assert len(debtors) == 0, "Przy wpłatach 2500 PLN lista dłużników za styczeń 2025 powinna być pusta."

def test_get_annual_summary():
    manager = Manager(Parameters())
    
    summary = manager.get_annual_summary(year=2025)
    
    assert isinstance(summary, dict), "Raport roczny powinien być słownikiem."
    assert "total_costs_pln" in summary, "Raport powinien zawierać całkowite koszty (rachunki mieszkania)."
    assert "total_incomes_pln" in summary, "Raport powinien zawierać całkowite przychody (wpłaty od lokatorów)."
    
    assert summary["total_costs_pln"] == 910.0, "Koszty dla 2025 roku powinny wynosić 910 PLN."
    assert summary["total_incomes_pln"] == 7500.0, "Wpłaty dla 2025 roku powinny wynosić 7500 PLN."

def test_get_tax():
    manager = Manager(Parameters())
    tax = manager.get_tax(year=2025, month=1, tax_rate=0.085)

    assert isinstance(tax, int), "Podatek powinien być zaokrąglony do pełnych złotych (typ int)."
    assert tax == 638, "Podatek od 7500 PLN przy stawce 8.5% powinien wynosić 638 PLN."

def test_get_annual_report():
    manager = Manager(Parameters())
    
    report = manager.get_annual_report(year=2025)
    
    assert isinstance(report, dict), "Raport powinien być słownikiem."
    assert report["total_costs_pln"] == 910.0, "Koszty dla 2025 r. powinny wynosić 910 PLN."
    assert report["total_incomes_pln"] == 7500.0, "Przychody dla 2025 r. powinny wynosić 7500 PLN."