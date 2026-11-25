/* BACS-Readiness-Check – TECHNE e.U. – App v1.0 (Daten nur lokal im Browser) */
(function () {
  'use strict';
  var K = window.KATALOG;
  var APPVER = '1.0';
  var KW = { D: 1, C: 2, B: 3, A: 4 };
  var KL = ['', 'D', 'C', 'B', 'A'];
  var LS = 'techne-rc-v1';
  var GNAME = {}; K.gewerke.forEach(function (g) { GNAME[g.k] = g.name; });
  var db = laden();
  var ui = { tab: 'objekt', nurOffen: false, suche: '' };

  // ------------------------------------------------------------ Speicher
  function laden() {
    try { var d = JSON.parse(localStorage.getItem(LS)); if (d && d.objs) return d; } catch (e) {}
    return { objs: {}, cur: null };
  }
  var saveTimer = null;
  function speichern(sofort) {
    clearTimeout(saveTimer);
    var tun = function () {
      try { localStorage.setItem(LS, JSON.stringify(db)); }
      catch (e) { toast('Speichern im Browser nicht möglich – bitte unter „Daten“ exportieren'); }
    };
    if (sofort) tun(); else saveTimer = setTimeout(tun, 300);
  }
  function heute() { var d = new Date(); return d.toISOString().slice(0, 10); }
  function neuesObjekt(name) {
    var id = 'o' + Date.now().toString(36) + Math.random().toString(36).slice(2, 5);
    db.objs[id] = { id: id, app: APPVER, katalog: K.version, name: name || 'Neues Objekt', land: '', art: 'Hotel',
      heiz: '', kaelte: '', fw: false, quelle: '', datum: heute(), begeher: '', notiz: '',
      aus: {}, f: {}, fa: {}, org1: '', org2: '', quick: '' };
    db.cur = id; speichern(true); return db.objs[id];
  }
  function cur() { return db.cur && db.objs[db.cur] ? db.objs[db.cur] : null; }

  // ------------------------------------------------------------ Hilfen
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function $(s, r) { return (r || document).querySelector(s); }
  function badge(k, gross) { return '<span class="kl kl-' + (k || 'offen') + (gross ? ' kl-gross' : '') + '">' + (k || '?') + '</span>'; }
  function toast(t) { var el = $('#toast'); el.textContent = t; el.classList.add('an'); clearTimeout(toast._t); toast._t = setTimeout(function () { el.classList.remove('an'); }, 2200); }
  function zahl(v) { var n = parseFloat(String(v).replace(',', '.')); return isNaN(n) ? null : n; }

  // ------------------------------------------------------------ Logik
  function fZustand(o, f) {
    var s = o.f[f.id] || {};
    if (o.aus[f.g]) return { rel: false, grund: 'Gewerk nicht vorhanden' };
    if (s.nv) return { rel: false, grund: 'Anlage nicht vorhanden' };
    if (s.lt5) return { rel: false, grund: 'unter 5 % Energieanteil' };
    if (s.wb) return { rel: false, grund: 'begründet weggelassen' };
    if (!s.typ) return { rel: true, k: null };
    var t = f.typ.filter(function (x) { return x.nr === s.typ; })[0];
    return { rel: true, k: t ? t.k : null, t: t };
  }
  function bZiel(f) {
    var t = f.typ.filter(function (x) { return KW[x.k] >= 3; })[0];
    if (!t) return null;
    return { t: t, ohneB: t.k === 'A' };
  }
  function bZielText(f) {
    var z = bZiel(f); if (!z) return '';
    return 'Für B: Typ ' + z.t.nr + ' – ' + z.t.text + (z.ohneB ? ' (keine eigene B-Stufe, A-Ausführung nötig)' : '');
  }
  function auswertung(o) {
    var r = { min: null, offen: 0, bewertet: 0, rel: 0, je: {}, luecken: [], irrel: [] };
    K.gewerke.forEach(function (g) { r.je[g.k] = { min: null, offen: 0, rel: 0, aus: !!o.aus[g.k] }; });
    K.funktionen.forEach(function (f) {
      var z = fZustand(o, f), j = r.je[f.g];
      if (!z.rel) { r.irrel.push({ f: f, grund: z.grund }); return; }
      r.rel++; j.rel++;
      if (!z.k) { r.offen++; j.offen++; return; }
      r.bewertet++;
      var w = KW[z.k];
      r.min = r.min == null ? w : Math.min(r.min, w);
      j.min = j.min == null ? w : Math.min(j.min, w);
      if (w < 3) r.luecken.push({ f: f, k: z.k, t: z.t });
    });
    return r;
  }
  function betroffenheit(o) {
    var H = zahl(o.heiz), C = zahl(o.kaelte), L = K.land[o.land] || null, out = [], stufe = '';
    if (H == null && C == null) return { stufe: 'offen', text: ['Leistung von Heizung und/oder Kühlung eintragen.'], land: L };
    var h = H || 0, c = C || 0, m = Math.max(h, c), s = h + c;
    if (m > 290) { stufe = '290';
      out.push('Über 290 kW: Pflicht zur Gebäudeautomation besteht bereits (EU-Frist 31.12.2024).');
      out.push('Automatische Beleuchtungssteuerung: Stichtag 31.12.2027.');
    } else if (m > 70) { stufe = '70';
      out.push('Über 70 kW: Gebäudeautomation, Stichtag 31.12.2029.');
      out.push('Automatische Beleuchtungssteuerung: Stichtag 31.12.2029.');
      if (s > 290) out.push('Heizung und Kühlung zusammen über 290 kW – Einordnung einzeln klären.');
    } else if (s > 70) { stufe = 'klaeren';
      out.push('Heizung und Kühlung liegen nur zusammen über 70 kW – Einordnung einzeln klären.');
    } else { stufe = 'unter';
      out.push('Bis 70 kW: keine Pflicht zur Gebäudeautomation nach Art. 13 EPBD; andere Vorgaben (z. B. beim Heizungstausch) gelten weiter.');
    }
    if (o.fw) out.push('Fernwärme: Leistung der Übergabestation (sekundär) bzw. Anschlussleistung laut Vertrag – rechtlich offen, konservativ angesetzt.');
    if (o.quelle === 'Angabe Kunde' || !o.quelle) out.push('Leistung noch belegen (Typenschild, Datenblatt oder Wärmeliefervertrag).');
    if (o.art && o.art.indexOf('gemischt') >= 0) out.push('Gemischte Nutzung: Einordnung als Nichtwohngebäude einzeln klären.');
    return { stufe: stufe, text: out, land: L };
  }
  function faehErgebnis(o, fa) {
    var st = fa.punkte.map(function (p) { return (o.fa[p.id] || {}).s || 'nicht geprüft'; });
    if (st.every(function (s) { return s === 'erfüllt'; })) return 'erfüllt';
    if (st.some(function (s) { return s === 'nicht erfüllt'; })) return 'nicht erfüllt';
    if (st.every(function (s) { return s === 'nicht geprüft'; })) return 'nicht geprüft';
    return 'teilweise / offen';
  }
  function lichtSteuerung(o) {
    var f = K.funktionen.filter(function (x) { return x.id === '5.1'; })[0], z = fZustand(o, f);
    if (!z.rel) return 'nicht beurteilt (' + z.grund + ')';
    if (!z.k) return 'offen';
    return (z.t.nr === '2' || z.t.nr === '3') ? 'Belegungserkennung vorhanden (Funktion 5.1)' : 'keine automatische Belegungserkennung (Funktion 5.1)';
  }

  // ------------------------------------------------------------ Rendern
  function render() {
    var sel = $('#objSel'), ids = Object.keys(db.objs);
    sel.innerHTML = ids.length ? ids.map(function (id) {
      var o = db.objs[id]; return '<option value="' + id + '"' + (id === db.cur ? ' selected' : '') + '>' + esc(o.name) + (o.datum ? ' · ' + esc(o.datum) : '') + '</option>';
    }).join('') : '<option value="">– noch kein Objekt –</option>';
    document.querySelectorAll('.tabs button').forEach(function (b) { b.classList.toggle('aktiv', b.getAttribute('data-tab') === ui.tab); });
    document.querySelectorAll('.tab').forEach(function (t) { t.classList.toggle('aktiv', t.id === 'tab-' + ui.tab); });
    var o = cur();
    if (!o) {
      var leer = '<div class="leer"><p>Noch kein Objekt angelegt.</p><button class="primaer" type="button" data-akt="neu">Erstes Objekt anlegen</button></div>';
      ['objekt', 'funktionen', 'faeh', 'auswertung'].forEach(function (t) { $('#tab-' + t).innerHTML = leer; });
      renderDaten(null); return;
    }
    renderObjekt(o); renderFunktionen(o); renderFaeh(o); renderAuswertung(o); renderDaten(o);
  }

  function feld(label, key, wert, typ, opts) {
    var id = 'f_' + key, h = '<div class="feld"><label for="' + id + '">' + label + '</label>';
    if (typ === 'select') h += '<select id="' + id + '" data-o="' + key + '">' + opts.map(function (x) { var v = x[0], t = x[1]; return '<option value="' + esc(v) + '"' + (String(wert) === v ? ' selected' : '') + '>' + esc(t) + '</option>'; }).join('') + '</select>';
    else if (typ === 'textarea') h += '<textarea id="' + id + '" data-o="' + key + '">' + esc(wert) + '</textarea>';
    else h += '<input id="' + id + '" data-o="' + key + '" type="' + (typ || 'text') + '" value="' + esc(wert) + '"' + (typ === 'number' ? ' inputmode="decimal" min="0" step="any"' : '') + '>';
    return h + '</div>';
  }

  function renderObjekt(o) {
    var b = betroffenheit(o), L = b.land, h = '';
    h += '<h2 class="unterstrich">Objekt und Betroffenheit</h2>';
    h += '<p class="hinweis">Kopfdaten und Leistung. Die Leistung immer belegen (Foto Typenschild bzw. Vertrag) – nicht übernehmen, was „man weiß“.</p>';
    h += '<div class="raster">';
    h += feld('Objekt (intern)', 'name', o.name);
    h += feld('Bundesland', 'land', o.land, 'select', [['', '– wählen –'], ['W', 'Wien'], ['N', 'Niederösterreich'], ['B', 'Burgenland'], ['X', 'anderes Bundesland']]);
    h += feld('Gebäudeart', 'art', o.art, 'select', [['Hotel', 'Hotel / Beherbergung'], ['Büro', 'Büro / Verwaltung'], ['Handel', 'Handel'], ['Gastronomie', 'Gastronomie'], ['Schule', 'Schule / Bildung'], ['sonstiges NWG', 'sonstiges Nichtwohngebäude'], ['gemischt', 'gemischt genutzt']]);
    h += feld('Wärmeleistung Heizung [kW]', 'heiz', o.heiz, 'number');
    h += feld('Kälteleistung Klima [kW]', 'kaelte', o.kaelte, 'number');
    h += feld('Leistung belegt durch', 'quelle', o.quelle, 'select', [['', '– wählen –'], ['Typenschild', 'Typenschild (Foto)'], ['Datenblatt', 'Datenblatt'], ['Wärmeliefervertrag', 'Wärmeliefervertrag'], ['Plan/Energieausweis', 'Plan / Energieausweis'], ['Angabe Kunde', 'nur Angabe Kunde']]);
    h += '<div class="feld"><label><input type="checkbox" data-o="fw"' + (o.fw ? ' checked' : '') + '> Fernwärme / Nahwärme</label></div>';
    h += feld('Datum Begehung', 'datum', o.datum, 'date');
    h += feld('Begangen von', 'begeher', o.begeher);
    h += '</div>';
    h += feld('Notizen zum Objekt (Zonen, Besonderheiten, Ansprechpartner vor Ort)', 'notiz', o.notiz, 'textarea');
    h += '<div class="box rahmen-rot ergebnis"><h3>Einordnung</h3>' + b.text.map(function (t) { return '<p>' + esc(t) + '</p>'; }).join('');
    if (L) {
      h += '<table><tr><th colspan="2">' + esc(L.name) + ' – ' + esc(L.gesetz) + '</th></tr>';
      [['über 290 kW', L.b290], ['über 70 kW', L.b70], ['Beleuchtungssteuerung', L.licht], ['Fähigkeiten', L.faeh], ['Vorbehalt', L.vorbehalt], ['Adressat', L.adressat], ['Inspektion', L.inspektion], ['Prüfstand Katalog', L.pruef]]
        .forEach(function (r) { h += '<tr><td>' + r[0] + '</td><td>' + esc(r[1]) + '</td></tr>'; });
      h += '</table>';
    }
    h += '<details class="pruef"><summary>Regeln zur Leistung</summary><ul class="liste">' + K.schwelle_hinweise.map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('') + '</ul></details>';
    h += '</div>';
    $('#tab-objekt').innerHTML = h;
  }

  function renderFunktionen(o) {
    var a = auswertung(o), h = '';
    h += '<h2 class="unterstrich">Funktionen je Gewerk</h2>';
    h += '<p class="hinweis">Je Funktion den Ist-Zustand wählen. Nicht vorhandene Anlagen, Anlagen unter 5 % Energieanteil und begründet weggelassene Funktionen zählen nicht. Die Gesamtklasse bestimmt die schwächste bewertete Funktion. ' +
      'Klasse je Typ = höchste in Nichtwohngebäuden erreichte Klasse; für C gilt der strengere Typ aus Tab. 6 und B.1.</p>';
    h += '<div class="filter"><input type="search" id="suche" placeholder="Funktion suchen …" value="' + esc(ui.suche) + '"><label><input type="checkbox" id="nurOffen"' + (ui.nurOffen ? ' checked' : '') + '> nur offene</label>' +
      '<span class="fortschritt">bewertet ' + a.bewertet + ' von ' + a.rel + ' relevanten · offen ' + a.offen + ' · vorläufig ' + badge(a.min ? KL[a.min] : null) + '</span></div>';
    var q = ui.suche.trim().toLowerCase();
    K.gewerke.forEach(function (g) {
      var j = a.je[g.k], fs = K.funktionen.filter(function (f) { return f.g === g.k; });
      var sicht = fs.filter(function (f) {
        if (q && (f.id + ' ' + f.t + ' ' + f.z).toLowerCase().indexOf(q) < 0) return false;
        if (ui.nurOffen) { var z = fZustand(o, f); return z.rel && !z.k; }
        return true;
      });
      if (!sicht.length && (q || ui.nurOffen)) return;
      var offen = (o._offen && o._offen[g.k]) || !!q || ui.nurOffen;
      h += '<details class="gewerk" data-g="' + g.k + '"' + (offen ? ' open' : '') + '><summary><span>' + esc(g.name) + ' <span class="fortschritt">(' + (j.aus ? 'nicht vorhanden' : (j.rel - j.offen) + '/' + j.rel + ' bewertet') + ')</span></span>' +
        '<span>' + (j.aus ? '' : badge(j.min ? KL[j.min] : null)) + '</span></summary>';
      h += '<div class="funktion"><label class="aus"><input type="checkbox" data-aus="' + g.k + '"' + (j.aus ? ' checked' : '') + '> Gewerk im Gebäude nicht vorhanden</label></div>';
      if (!j.aus) sicht.forEach(function (f) { h += funktionHtml(o, f); });
      h += '</details>';
    });
    $('#tab-funktionen').innerHTML = h;
  }

  function funktionHtml(o, f) {
    var s = o.f[f.id] || {}, z = fZustand(o, f), h = '';
    h += '<div class="funktion' + (z.rel ? '' : ' irrelevant') + '" id="fn-' + f.id.replace('.', '_') + '">';
    h += '<div class="fkopf"><div><span class="nr">Funktion ' + f.id + ' · EN ISO 52120-1 Tab. 6</span><h4>' + esc(f.t) + '</h4></div><div>' + (z.rel ? badge(z.k) : '<span class="hinweis">' + esc(z.grund) + '</span>') + '</div></div>';
    h += '<p class="zweck">' + esc(f.z) + '</p>';
    h += '<details class="pruef"><summary>Woran erkennst du es vor Ort?</summary><p>' + esc(f.p) + '</p>' + (f.h ? '<p><strong>Praxis:</strong> ' + esc(f.h) + '</p>' : '') + (f.n ? '<p class="notiz-n">Normhinweis: ' + esc(f.n) + '</p>' : '') + '</details>';
    h += '<div class="flags">' +
      '<label><input type="checkbox" data-f="' + f.id + '" data-k="nv"' + (s.nv ? ' checked' : '') + '> Anlage nicht vorhanden</label>' +
      '<label><input type="checkbox" data-f="' + f.id + '" data-k="lt5"' + (s.lt5 ? ' checked' : '') + '> unter 5 % Energieanteil</label>' +
      '<label><input type="checkbox" data-f="' + f.id + '" data-k="wb"' + (s.wb ? ' checked' : '') + '> begründet weglassen</label></div>';
    if (s.wb || s.lt5) h += '<div class="feld"><label>Begründung (für den Bericht)</label><input data-f="' + f.id + '" data-k="wbText" value="' + esc(s.wbText) + '"></div>';
    if (!s.nv && !s.wb && !s.lt5) {
      h += '<div class="typen" role="radiogroup" aria-label="Ist-Zustand ' + esc(f.t) + '">';
      f.typ.forEach(function (t) {
        h += '<label><input type="radio" name="t_' + f.id + '" data-f="' + f.id + '" data-k="typ" value="' + esc(t.nr) + '"' + (s.typ === t.nr ? ' checked' : '') + '>' +
          '<span class="nr">' + esc(t.nr) + '</span><span class="ttext">' + esc(t.text) + '</span>' + badge(t.k) + '</label>';
      });
      h += '</div>';
      if (s.typ) h += '<button type="button" class="klein" data-f="' + f.id + '" data-akt="typweg">Auswahl zurücksetzen</button>';
    }
    h += '<p class="ziel">' + esc(bZielText(f)) + ' · zuständig: ' + esc(f.w) + '</p>';
    h += '<div class="zeile2"><div class="feld"><label>Befund (Stichworte)</label><textarea data-f="' + f.id + '" data-k="notiz">' + esc(s.notiz) + '</textarea></div>' +
      '<div class="feld"><label>Maßnahme / Foto-Nr.</label><textarea data-f="' + f.id + '" data-k="mass">' + esc(s.mass) + '</textarea></div></div>';
    return h + '</div>';
  }

  function renderFaeh(o) {
    var h = '<h2 class="unterstrich">Fähigkeiten a–d (Rechtspflicht)</h2>';
    h += '<p class="hinweis">Getrennt von der Klasse: Das Gesetz verlangt vier Fähigkeiten (EPBD Art. 13 Abs. 10; Wien § 14b Abs. 2, NÖ § 44a Abs. 5, Bgld. § 34g Abs. 7). Eine Fähigkeit ist erfüllt, wenn alle Prüfpunkte erfüllt sind. Prüfpunkte sinngemäß; mit „TECHNE-Prüfmaßstab“ markierte Werte sind Praxiswerte, kein Gesetzeswortlaut.</p>';
    K.faehigkeiten.forEach(function (fa) {
      var e = faehErgebnis(o, fa);
      h += '<div class="box"><div class="fkopf"><h3 style="margin:0">' + esc(fa.t) + '</h3><strong>' + esc(e) + '</strong></div><p class="zweck">' + esc(fa.z) + '</p><table><tr><th>Prüfpunkt</th><th style="width:150px">Status</th><th>Befund</th></tr>';
      fa.punkte.forEach(function (p) {
        var s = o.fa[p.id] || {};
        h += '<tr><td><span class="nr">' + p.id + '</span> ' + esc(p.t) + (p.m ? '<div class="masstab">' + esc(p.m) + '</div>' : '') + '</td><td><select class="status-sel" data-fa="' + p.id + '" data-k="s">' +
          K.faeh_status.map(function (st) { return '<option' + ((s.s || 'nicht geprüft') === st ? ' selected' : '') + '>' + st + '</option>'; }).join('') +
          '</select></td><td><input data-fa="' + p.id + '" data-k="n" value="' + esc(s.n) + '" style="width:100%;padding:6px;border:1px solid #404040;border-radius:4px"></td></tr>';
      });
      h += '</table></div>';
    });
    h += '<div class="box"><h3 style="margin-top:0">Organisation (Klasse B scheitert öfter an der Zuständigkeit als an der Technik)</h3><div class="zeile2">' +
      feld('Wer reagiert auf Störmeldungen und Alarme?', 'org1', o.org1, 'textarea') + feld('Wer pflegt Zeitprogramme und Sollwerte?', 'org2', o.org2, 'textarea') + '</div></div>';
    $('#tab-faeh').innerHTML = h;
  }

  function renderAuswertung(o) {
    var a = auswertung(o), b = betroffenheit(o), h = '';
    var gesamt = a.min ? KL[a.min] : null;
    h += '<h2 class="unterstrich">Auswertung – ' + esc(o.name) + '</h2>';
    h += '<p class="hinweis">Stand ' + esc(o.datum || '') + (o.begeher ? ' · begangen von ' + esc(o.begeher) : '') + ' · Katalog v' + esc(K.version) + '</p>';
    h += '<div class="box rahmen-rot"><div class="fkopf"><div><h3 style="margin-top:0">Gesamtklasse (Ist)</h3><p>' +
      (a.offen ? 'Vorläufig – ' + a.offen + ' relevante Funktion(en) noch nicht bewertet.' : (a.bewertet ? 'Alle relevanten Funktionen bewertet.' : 'Noch keine Funktion bewertet.')) +
      '</p><p class="hinweis">Gesamtklasse = schwächste bewertete Funktion (EN ISO 52120-1, 5.6). Ziel TECHNE: Klasse B.</p></div>' + badge(gesamt, true) + '</div></div>';
    h += '<h3>Einordnung</h3><ul class="liste">' + b.text.map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('') + '</ul>';
    if (b.land) h += '<p class="hinweis">' + esc(b.land.name) + ': ' + esc(b.land.gesetz) + ' (' + esc(b.land.pruef) + ')</p>';
    h += '<h3>Klasse je Gewerk</h3><table><tr><th>Gewerk</th><th>Klasse</th><th>bewertet</th></tr>';
    K.gewerke.forEach(function (g) {
      var j = a.je[g.k];
      h += '<tr><td>' + esc(g.name) + '</td><td>' + (j.aus ? 'nicht vorhanden' : badge(j.min ? KL[j.min] : null)) + '</td><td>' + (j.aus ? '–' : (j.rel - j.offen) + ' von ' + j.rel) + '</td></tr>';
    });
    h += '</table>';
    h += '<h3>Fähigkeiten a–d</h3><table><tr><th>Fähigkeit</th><th>Ergebnis</th></tr>';
    K.faehigkeiten.forEach(function (fa) { h += '<tr><td>' + esc(fa.t) + '</td><td>' + esc(faehErgebnis(o, fa)) + '</td></tr>'; });
    h += '<tr><td>Automatische Beleuchtungssteuerung</td><td>' + esc(lichtSteuerung(o)) + '</td></tr></table>';
    h += '<h3>Lücken zu Klasse B (' + a.luecken.length + ')</h3>';
    if (a.luecken.length) {
      h += '<table><tr><th>Nr.</th><th>Funktion</th><th>Ist</th><th>Für Klasse B nötig</th><th>Zuständig</th><th>Befund / Maßnahme</th></tr>';
      a.luecken.forEach(function (l) {
        var s = o.f[l.f.id] || {}, z = bZiel(l.f);
        h += '<tr><td class="nr">' + l.f.id + '</td><td>' + esc(l.f.t) + '</td><td>' + badge(l.k) + ' ' + esc(l.t ? l.t.text : '') + '</td><td>' +
          (z ? 'Typ ' + esc(z.t.nr) + ' – ' + esc(z.t.text) + (z.ohneB ? ' <em>(A-Ausführung, keine B-Stufe)</em>' : '') : '') + '</td><td>' + esc(l.f.w) + '</td><td>' + esc([s.notiz, s.mass].filter(Boolean).join(' · ')) + '</td></tr>';
      });
      h += '</table>';
    } else h += '<p>Keine bewertete Funktion unter Klasse B.</p>';
    if (a.irrel.length) {
      h += '<h3>Nicht berücksichtigt (' + a.irrel.length + ')</h3><table><tr><th>Nr.</th><th>Funktion</th><th>Grund</th></tr>';
      a.irrel.forEach(function (x) { var s = o.f[x.f.id] || {}; h += '<tr><td class="nr">' + x.f.id + '</td><td>' + esc(x.f.t) + '</td><td>' + esc(x.grund) + (s.wbText ? ': ' + esc(s.wbText) : '') + '</td></tr>'; });
      h += '</table>';
    }
    h += '<div class="feld"><label for="f_quick">Sofortmaßnahmen ohne Investition (Zeitprogramme, Sollwerte, Hand → Automatik)</label><textarea id="f_quick" data-o="quick">' + esc(o.quick) + '</textarea></div>';
    if (o.org1 || o.org2) h += '<h3>Organisation</h3><p>Störungen: ' + esc(o.org1 || '–') + '<br>Zeitprogramme/Sollwerte: ' + esc(o.org2 || '–') + '</p>';
    h += '<div class="knopfreihe"><button type="button" class="primaer" data-akt="drucken">Drucken / als PDF speichern</button><button type="button" data-akt="csv">Tabelle als CSV</button></div>';
    $('#tab-auswertung').innerHTML = h;
  }

  function renderDaten(o) {
    var h = '<h2 class="unterstrich">Daten</h2>';
    h += '<p>Alle Eingaben liegen nur in diesem Browser auf diesem Gerät. Nach jeder Begehung exportieren und die Datei im Projektordner ablegen (Ordner 02/Unterlagen bzw. laut Projekt). Ein Export lässt sich auf jedem Gerät wieder importieren.</p>';
    h += '<div class="knopfreihe">' +
      (o ? '<button type="button" class="primaer" data-akt="export">Objekt exportieren (JSON)</button><button type="button" data-akt="csv">Funktionen als CSV</button><button type="button" data-akt="kopie">Objekt kopieren</button>' : '') +
      '<label class="nodruck" style="display:inline-flex;align-items:center;gap:6px;border:1px solid #000;border-radius:4px;padding:8px 12px;cursor:pointer">Importieren (JSON)<input type="file" id="imp" accept=".json,application/json" style="display:none"></label>' +
      (o ? '<button type="button" data-akt="loeschen">Objekt löschen</button>' : '') + '</div>';
    h += '<h3>Objekte auf diesem Gerät</h3><table><tr><th>Objekt</th><th>Datum</th><th>Gesamt (Ist)</th></tr>';
    Object.keys(db.objs).forEach(function (id) {
      var x = db.objs[id], a = auswertung(x);
      h += '<tr><td><a href="#" data-akt="wechsel" data-id="' + id + '">' + esc(x.name) + '</a></td><td>' + esc(x.datum) + '</td><td>' + badge(a.min ? KL[a.min] : null) + (a.offen ? ' vorläufig' : '') + '</td></tr>';
    });
    h += '</table>';
    h += '<p class="hinweis">Datenschutz: keine Kundendaten in Dateinamen außerhalb der Projektablage; Exporte nicht per Messenger verteilen.</p>';
    $('#tab-daten').innerHTML = h;
    var inp = $('#imp'); if (inp) inp.addEventListener('change', importieren);
  }

  // ------------------------------------------------------------ Export / Import
  function datei(name, inhalt, mime) {
    var bl = new Blob([inhalt], { type: mime }), a = document.createElement('a');
    a.href = URL.createObjectURL(bl); a.download = name; document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }
  function dname(o, ext) { return 'Readiness-Check_' + (o.name || 'Objekt').replace(/[^\wäöüÄÖÜß-]+/g, '-').replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/Ä/g, 'Ae').replace(/Ö/g, 'Oe').replace(/Ü/g, 'Ue').replace(/ß/g, 'ss') + '_' + (o.datum || heute()).replace(/-/g, '').slice(2) + '.' + ext; }
  function exportieren(o) { o.app = APPVER; o.katalog = K.version; datei(dname(o, 'json'), JSON.stringify({ typ: 'techne-readiness-check', version: 1, objekt: o }, null, 1), 'application/json'); }
  function csv(o) {
    var z = [['Nr', 'Gewerk', 'Funktion', 'Status', 'Typ', 'Ist-Typ', 'Klasse', 'Fuer B noetig', 'Zustaendig', 'Befund', 'Massnahme/Foto', 'Begruendung']];
    K.funktionen.forEach(function (f) {
      var s = o.f[f.id] || {}, st = fZustand(o, f);
      z.push([f.id, GNAME[f.g], f.t, st.rel ? (st.k ? 'bewertet' : 'offen') : st.grund, s.typ || '', st.t ? st.t.text : '', st.k || '', bZielText(f), f.w, s.notiz || '', s.mass || '', s.wbText || '']);
    });
    var txt = '﻿' + z.map(function (r) { return r.map(function (c) { c = String(c).replace(/"/g, '""'); return /[;"\n]/.test(c) ? '"' + c + '"' : c; }).join(';'); }).join('\r\n');
    datei(dname(o, 'csv'), txt, 'text/csv;charset=utf-8');
  }
  function importieren(e) {
    var fl = e.target.files && e.target.files[0]; if (!fl) return;
    var r = new FileReader();
    r.onload = function () {
      try {
        var d = JSON.parse(r.result), o = d.objekt || d;
        if (!o || typeof o.f !== 'object' || !o.id) throw new Error('kein Readiness-Check-Export');
        if (db.objs[o.id] && !confirm('Objekt „' + o.name + '“ ist schon vorhanden. Überschreiben?')) { o.id = o.id + 'k' + Date.now().toString(36); o.name += ' (Import)'; }
        o.aus = o.aus || {}; o.fa = o.fa || {};
        db.objs[o.id] = o; db.cur = o.id; speichern(true); render(); toast('Importiert: ' + o.name);
      } catch (err) { toast('Import fehlgeschlagen: ' + err.message); }
    };
    r.readAsText(fl, 'utf-8');
  }

  // ------------------------------------------------------------ Ereignisse
  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-tab],[data-akt]'); if (!t) return;
    if (t.hasAttribute('data-tab')) { ui.tab = t.getAttribute('data-tab'); render(); window.scrollTo(0, 0); return; }
    var akt = t.getAttribute('data-akt'), o = cur();
    if (akt === 'neu') { neuesObjekt(); ui.tab = 'objekt'; render(); return; }
    if (akt === 'wechsel') { e.preventDefault(); db.cur = t.getAttribute('data-id'); speichern(true); ui.tab = 'objekt'; render(); return; }
    if (!o) return;
    if (akt === 'typweg') { var id = t.getAttribute('data-f'); if (o.f[id]) delete o.f[id].typ; speichern(); render(); }
    else if (akt === 'export') exportieren(o);
    else if (akt === 'csv') csv(o);
    else if (akt === 'drucken') { ui.tab = 'auswertung'; render(); setTimeout(function () { window.print(); }, 100); }
    else if (akt === 'kopie') { var c = JSON.parse(JSON.stringify(o)); c.id = 'o' + Date.now().toString(36); c.name = o.name + ' (Kopie)'; db.objs[c.id] = c; db.cur = c.id; speichern(true); render(); toast('Kopie angelegt'); }
    else if (akt === 'loeschen') { if (confirm('Objekt „' + o.name + '“ auf diesem Gerät löschen? Vorher exportieren!')) { delete db.objs[o.id]; db.cur = Object.keys(db.objs)[0] || null; speichern(true); render(); } }
  });
  document.addEventListener('toggle', function (e) {
    var d = e.target; if (!d.classList || !d.classList.contains('gewerk')) return;
    var o = cur(); if (!o) return; o._offen = o._offen || {}; o._offen[d.getAttribute('data-g')] = d.open; speichern();
  }, true);
  function eingabe(e, endgueltig) {
    var el = e.target, o = cur(); if (!o) return;
    var wert = el.type === 'checkbox' ? el.checked : el.value, neu = false;
    if (el.id === 'suche') { ui.suche = el.value; if (endgueltig) renderFunktionen(o); return; }
    if (el.id === 'nurOffen') { ui.nurOffen = el.checked; renderFunktionen(o); return; }
    if (el.hasAttribute('data-o')) { o[el.getAttribute('data-o')] = wert; neu = el.tagName === 'SELECT' || el.type === 'checkbox' || el.type === 'number' || el.type === 'date'; if (el.getAttribute('data-o') === 'name') $('#objSel').options[$('#objSel').selectedIndex].text = wert; }
    else if (el.hasAttribute('data-aus')) { o.aus[el.getAttribute('data-aus')] = wert; neu = true; }
    else if (el.hasAttribute('data-f')) { var id = el.getAttribute('data-f'), k = el.getAttribute('data-k'); o.f[id] = o.f[id] || {}; o.f[id][k] = wert; neu = k === 'typ' || k === 'nv' || k === 'lt5' || k === 'wb'; }
    else if (el.hasAttribute('data-fa')) { var p = el.getAttribute('data-fa'); o.fa[p] = o.fa[p] || {}; o.fa[p][el.getAttribute('data-k')] = wert; neu = el.tagName === 'SELECT'; }
    else return;
    speichern();
    if (neu && endgueltig) {
      var y = window.scrollY, fokus = document.activeElement && document.activeElement.id;
      setTimeout(function () { if (fokus) { var fe = document.getElementById(fokus); if (fe && fe !== document.activeElement) fe.focus(); } }, 0);
      if (ui.tab === 'objekt') renderObjekt(o); else if (ui.tab === 'funktionen') renderFunktionen(o); else if (ui.tab === 'faeh') renderFaeh(o); else if (ui.tab === 'auswertung') renderAuswertung(o);
      window.scrollTo(0, y);
    }
  }
  document.addEventListener('input', function (e) { eingabe(e, false); if (e.target.id === 'suche') { clearTimeout(eingabe._t); eingabe._t = setTimeout(function () { renderFunktionen(cur()); var s = $('#suche'); if (s) { s.focus(); s.setSelectionRange(s.value.length, s.value.length); } }, 350); } });
  document.addEventListener('change', function (e) { eingabe(e, true); });
  $('#objSel').addEventListener('change', function (e) { if (e.target.value) { db.cur = e.target.value; speichern(true); render(); } });
  $('#btnNeu').addEventListener('click', function () { neuesObjekt(); ui.tab = 'objekt'; render(); var n = $('#f_name'); if (n) { n.focus(); n.select(); } });
  window.addEventListener('beforeunload', function () { speichern(true); });

  // ------------------------------------------------------------ Start
  $('#versionInfo').textContent = 'App v' + APPVER + ' · Katalog v' + K.version + ' (Stand ' + K.stand + ') · ' + K.norm;
  render();
  if ('serviceWorker' in navigator && location.protocol === 'https:') navigator.serviceWorker.register('sw.js').catch(function () {});
  window.RC_TEST = { auswertung: auswertung, betroffenheit: betroffenheit, fZustand: fZustand, bZiel: bZiel, faehErgebnis: faehErgebnis, db: function () { return db; }, neu: neuesObjekt, render: render };
})();
