
def InventarioFisicoNewFolio():
    from django_microsip_base.libs.models_base.models import Registry
    
    registro = Registry.objects.get( nombre = 'SIG_FOLIO_INVFIS' )
    new_folio = "%09d" % ( int( registro.valor ) +1 )
    registro.valor = new_folio
    registro.save()
    return new_folio