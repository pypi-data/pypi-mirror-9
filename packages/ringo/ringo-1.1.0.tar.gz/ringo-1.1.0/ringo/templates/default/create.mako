<%inherit file="/main.mako" />
<div class="page-header">
  <div class="row">
    <div class="col-md-8">
      <h1>${_('New')} ${_(h.get_item_modul(request, clazz).get_label())}</h1>
    </div>
    <div class="col-md-4">
    </div>
  </div>
</div>
<div class="row">
  <div class="col-md-12">
    ${form | n}
  </div>
</div>
