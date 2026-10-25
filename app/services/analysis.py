from decimal import Decimal, ROUND_HALF_UP
from app.models.validation import day, rows, text, number

def analyze(payload):
    today=day(payload.get('as_of')); inventory=rows(payload.get('inventory'))
    # Demanda mensual compartida por SKU: se distribuye una sola vez en orden FEFO.
    demand=payload.get('monthly_demand')
    if not isinstance(demand,dict): raise ValueError('monthly_demand debe mapear SKU a unidades/mes')
    demand={text(k,'sku'):number(v,'monthly_demand') for k,v in demand.items()}
    lots=[];seen=set()
    for r in inventory:
        sku=text(r.get('sku'),'sku');lot=text(r.get('lot'),'lot')
        if (sku,lot) in seen: raise ValueError('SKU/lote duplicado; consolidar almacenes previamente')
        seen.add((sku,lot))
        if sku not in demand: raise ValueError(f'Falta demanda mensual para {sku}')
        qty=number(r.get('quantity'),'quantity',True);cost=number(r.get('unit_cost'),'unit_cost')
        status=r.get('status','available')
        if status not in ['available','blocked']: raise ValueError('status debe ser available o blocked')
        lots.append(dict(sku=sku,lot=lot,quantity=qty,cost=cost,expiry=day(r.get('expiry')),status=status))
    findings=[];items=[];allocated={};total=Decimal(0)
    def money(n):return str(n.quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
    for r in sorted(lots,key=lambda x:(x['sku'],x['expiry'],x['lot'])):
        sku=r['sku'];qty=r['quantity'];days=(r['expiry']-today).days
        code=None;severity='media';rem=Decimal(qty)
        if qty==0: rem=Decimal(0)
        elif days<=0: code='EXPIRED';severity='critica'
        elif r['status']=='blocked':code='BLOCKED';severity='alta'
        else:
            horizon=demand[sku]*Decimal(days)/Decimal(30)
            capacity=max(Decimal(0),horizon-allocated.get(sku,Decimal(0)))
            consumed=min(Decimal(qty),capacity)
            allocated[sku]=allocated.get(sku,Decimal(0))+consumed
            rem=Decimal(qty)-consumed
            if days<=90:code='NEAR_EXPIRY';severity='alta' if rem>0 else 'media'
            elif rem>0:code='SLOW_ROTATION';severity='media'
        exposure=rem*r['cost'];total+=exposure
        source=f'inventory/{sku}/{r["lot"]} + monthly_demand/{sku}'
        item={'sku':sku,'lot':r['lot'],'days':days,'quantity':qty,'estimated_remaining':str(rem.quantize(Decimal('.01'))),
              'exposure_pen':money(exposure),'status':r['status'],'expiry':r['expiry'].isoformat()}
        items.append(item)
        if code:
            action='Segregar y escalar al responsable; sin propuesta de despacho.' if code in ['EXPIRED','BLOCKED'] else 'Revisar rotación, reposición y condiciones documentadas de devolución; cualquier despacho requiere elegibilidad.'
            findings.append(dict(id=f'F{len(findings)+1}',code=code,severity=severity,source=source,
                message=f'{sku}/{r["lot"]}: {days} días al vencimiento; exposición estimada S/ {money(exposure)}. {action}'))
    return {'title':'Priorización de vencimientos','as_of':today.isoformat(),
            'metrics':{'lotes':len(lots),'observaciones':len(findings),'exposicion_pen':money(total)},
            'findings':findings,'items':items,'decision':'Estimación operativa para revisión humana'}
