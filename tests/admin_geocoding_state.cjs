const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
class Element {
  constructor() { this.children = []; this.value = ''; this.handlers = {}; this.dataset = {}; this.classList = {add(){}}; this.open = false; }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; }
  setAttribute(k,v) { this[k] = v; }
  removeAttribute(k) { delete this[k]; }
  addEventListener(k,v) { this.handlers[k] = v; }
  querySelector() { return null; }
  focus() {}
  showModal() { this.open = true; }
  close() { this.open = false; }
}
const ctx = vm.createContext({assert, Element, console});
vm.runInContext(fs.readFileSync('web/admin.js','utf8'),ctx);
vm.runInContext(`
  document = {createElement: () => new Element()};
  window = {confirm: () => true};
  for (const id of ['geocode-dialog','geocode-dialog-title','geocode-query','geocode-candidates',
    'geocode-empty','geocode-error','geocode-confirm','geocode-replace-warning','geocode-cancel',
    'location-institution-id','location-geocode','location-form-error','confirmed-lat','confirmed-lon',
    'confirmed-city','confirmed-region','confirmed-country','confirmed-country-code']) elements[id] = new Element();
  state.selectedInstitutionLocationId = 'hkbu';
  elements['location-institution-id'].value = 'hkbu';
  const safe = {institution_name:'Hong Kong Baptist University', city:'Hong Kong',region:'Hong Kong',country:'China',country_code:'CN',latitude:22.338,longitude:114.182,selectable:true,conflicts:[]};
  const bad = {...safe,selectable:false,conflicts:['provider district conflicts with campus locality evidence']};
  const disabled = () => {assert.equal(elements['geocode-confirm'].disabled,true); assert.equal(elements['geocode-confirm']['aria-disabled'],'true');};
  const select = index => {const radio=elements['geocode-candidates'].children[index].children[0];radio.checked=true;radio.handlers.change();};
  const pristine = () => assert.equal(elements['confirmed-lat'].value,'');
  renderGeocodeCandidates({candidates:[bad],no_safe_match:true}); disabled();
  select(0); disabled(); confirmGeocodeCandidate(); pristine();
  renderGeocodeCandidates({candidates:[safe,bad]}); disabled(); confirmGeocodeCandidate(); pristine();
  select(0); assert.equal(elements['geocode-confirm'].disabled,false);
  select(1); disabled(); confirmGeocodeCandidate(); pristine();
  select(0); assert.equal(elements['geocode-confirm'].disabled,false);
  safe.selectable=false; confirmGeocodeCandidate(); disabled(); pristine(); safe.selectable=true;
  renderGeocodeCandidates({candidates:[safe]});select(0);
  const staleRadio=elements['geocode-candidates'].children[0].children[0];
  renderGeocodeCandidates({candidates:[]});disabled();staleRadio.handlers.change();disabled();confirmGeocodeCandidate();pristine();
  renderGeocodeCandidates({candidates:[safe]});select(0);closeGeocodeDialog();disabled();confirmGeocodeCandidate();pristine();
  renderGeocodeCandidates({candidates:[safe]});disabled();select(0);
  state.selectedInstitutionLocationId='other';confirmGeocodeCandidate();disabled();pristine();state.selectedInstitutionLocationId='hkbu';
  renderGeocodeCandidates({candidates:[safe]});select(0);confirmGeocodeCandidate();assert.equal(elements['confirmed-lat'].value,22.338);disabled();
  elements['confirmed-lat'].value='';elements['confirmed-lon'].value='';
  renderGeocodeCandidates({candidates:[safe]});select(0);
  let finish; apiFetch = () => new Promise(resolve => {finish=resolve;});
  const pending = findInstitutionCoordinates();disabled();confirmGeocodeCandidate();pristine();
  finish({data:{institution_id:'hkbu',candidates:[]}});
  pending.then(() => {disabled();pristine();console.log('geocoding state regression checks passed');});
`,ctx);
