(function($) {
    $(document).ready(function($) {

        $('td.field-unit_price input').keyup(function() {
            p = (this.id);
            n = p.indexOf("-");
            t = p.indexOf("-unit_price");
            c = p.substring(n+1, t);
            if ($('#id_line-'+c+'-quantity').val().length > 0 && isNaN($('#id_line-'+c+'-quantity').val()) == false) {
              res = $('#id_line-'+c+'-quantity').val() * $('#id_line-'+c+'-unit_price').val()
              $('#id_line-'+c+'-amount').val(res);
            }
            var subtotal = 0
            var subtotal_taxes = 1
            var subtotal_retentions = 1
            $('[id^="id_line"][id$="amount"]').each(function() {
                subtotal += Number($(this).val());
                $('#id_subtotal').val(subtotal);
                taxes = $('#id_taxes option:selected').text();
                taxes = taxes.replace('%','')/100;
                subtotal_taxes = (subtotal*taxes)*100/100
                $('#id_subtotal_iva').val(subtotal_taxes);
                retentions = $('#id_retentions option:selected').text();
                retentions = Number(retentions.replace('%',''))/100*-1;
                subtotal_retentions = (subtotal*retentions)*100/100
                $('#id_subtotal_retentions').val(subtotal_retentions);
                $('#id_total').val((subtotal+subtotal_taxes+subtotal_retentions)*100/100);
            });
        });

    });
})(django.jQuery);