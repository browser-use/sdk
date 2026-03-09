// Set data-product attribute on <html> for CSS targeting
(function () {
  function setProduct() {
    var p = location.pathname.startsWith('/open-source') ? 'open-source' : 'cloud';
    document.documentElement.setAttribute('data-product', p);
  }
  setProduct();
  window.addEventListener('popstate', setProduct);
  new MutationObserver(function () { setProduct(); })
    .observe(document.documentElement, { childList: true, subtree: true });
})();
