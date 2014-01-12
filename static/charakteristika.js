$(document).ready(function(){
    $('form').each(function() {
      this.charakteristikaOriginalSerialized = $(this).serialize();
      this.dirty = function() {
        return $(this).serialize() != this.charakteristikaOriginalSerialized;
      }
      this.submitting = false;
      $(this).on('submit', function() {
        this.submitting = true;
      });
    });
    $(window).on('beforeunload', function() {
      var form = document.getElementById('deform');
      if (form.dirty() && !form.submitting) {
        return "Vo formulári máte neuložené zmeny, po odchode zo stránky sa stratia. Naozaj chcete odísť zo stránky?";
      }
      form.submitting = false;
    });
});