/* SJ Interiors Admin — Client-side behaviors */

// HTMX loading bar
document.addEventListener('htmx:beforeRequest', function() {
  document.getElementById('admin-loading-bar').style.opacity = '1';
});
document.addEventListener('htmx:afterRequest', function() {
  document.getElementById('admin-loading-bar').style.opacity = '0';
});

// Dynamic line items builder for documents
window.addDocumentItemRow = function() {
  const container = document.getElementById('document-items-container');
  if (!container) return;
  const row = document.createElement('div');
  row.className = 'row align-items-center g-2 doc-item-row';
  row.innerHTML = `
    <div class="col-12 col-md-3 mb-2">
      <input type="text" name="item_category[]" placeholder="Category Group (e.g. 1. SITTING ROOM CURTAINS)" class="form-control form-control-sm">
    </div>
    <div class="col-12 col-md-3 mb-2">
      <input type="text" name="item_desc[]" placeholder="Item name (e.g. Yards of Curtain)" required class="form-control form-control-sm">
    </div>
    <div class="col-12 col-md-2 mb-2">
      <input type="text" name="item_spec[]" placeholder="Spec / Details" class="form-control form-control-sm">
    </div>
    <div class="col-6 col-md-1 mb-2">
      <input type="number" name="item_qty[]" value="1" step="0.5" min="0.5" placeholder="Qty" required class="form-control form-control-sm">
    </div>
    <div class="col-6 col-md-2 mb-2">
      <input type="number" name="item_price[]" value="0" step="100" min="0" placeholder="Price" required class="form-control form-control-sm">
    </div>
    <div class="col-12 col-md-1 mb-2">
      <button type="button" class="btn btn-outline-danger btn-sm w-100" onclick="this.closest('.row').remove();">
        <i class="bi bi-x-lg"></i>
      </button>
    </div>
  `;
  container.appendChild(row);
};

// ─────────────────────────────────────────────────────────────────────────────
// Auto-slug generation for inputs with data-slug-source="true"
// The target slug input id is specified via data-slug-target="<id>"
// ─────────────────────────────────────────────────────────────────────────────
function _toSlug(text) {
  return text
    .toLowerCase()
    .trim()
    .replace(/[&]/g, 'and')
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

document.addEventListener('htmx:afterSwap', _bindSlugListeners);
document.addEventListener('DOMContentLoaded', _bindSlugListeners);

function _bindSlugListeners() {
  document.querySelectorAll('[data-slug-source="true"]').forEach(function(src) {
    if (src._slugBound) return;
    src._slugBound = true;
    src.addEventListener('input', function() {
      const targetId = src.getAttribute('data-slug-target');
      if (!targetId) return;
      const target = document.getElementById(targetId);
      if (!target || target.value) return; // Don't overwrite if user typed a slug
      target.value = _toSlug(src.value);
    });
    // Also allow clearing the slug to auto-regenerate
    const targetId = src.getAttribute('data-slug-target');
    if (targetId) {
      const target = document.getElementById(targetId);
      if (target) {
        target.addEventListener('focus', function() {
          target._userEdited = true;
        });
        // Override: if target was cleared, re-enable auto-fill
        target.addEventListener('input', function() {
          if (!target.value) target._userEdited = false;
        });
      }
    }
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Media Library Picker — fills the field identified by window.currentMediaTarget
// Called from bootstrap modal when admin clicks an image thumbnail
// ─────────────────────────────────────────────────────────────────────────────
window.selectMediaForTarget = function(url) {
  const targetId = window.currentMediaTarget;
  if (!targetId) return;
  const el = document.getElementById(targetId);
  if (el) {
    el.value = url;
    el.dispatchEvent(new Event('input', { bubbles: true }));
  }
  // Close the modal
  const modal = document.getElementById('mediaPickerModal');
  if (modal) {
    const bsModal = bootstrap.Modal.getInstance(modal);
    if (bsModal) bsModal.hide();
  }
  window.currentMediaTarget = null;
};
