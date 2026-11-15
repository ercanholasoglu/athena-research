---
title: "Önceden kayda geçirilmiş bir model konseyi deneyi: en iyi tek model kazandı. Bunun ne anlama geldiği ve gelmediği."
result: REJECTED_ON_THIS_BENCHMARK
date_of_experiment: 2026-11-04
evidence: ../EVIDENCE_MAP.md · ../evidence/council/results.json · ../notebooks/03_council_judge_critic.ipynb
---

Çok modelli "konsey" kolay anlatılan bir hikâyedir: birkaç modele sorulur, oylarlar ya da tartışırlar ve cevap
iyileşir. Bu hikâyenin Athena'nın ürün iddialarına yaklaşmasına izin verilmeden önce hikâye, Athena'nın gerçekten
cevaplaması gereken sorular üzerinde test edildi:
- Bu kolon sızıntı (leakage) mı, korunan bir özelliğin vekili mi, yoksa sorunsuz mu?
- Bu neredeyse kusursuz skor inandırıcı mı?
- Belirli bir politikaya göre hangi model seçilmeli?

Hipotezler, koşullar, metrikler ve karar kuralları *ilk model çağrısından önce* yazıldı ve repository'ye
işlendi (`protocol/PREREGISTRATION.md`). Planda iki sorun çıktı. İkisi de herhangi bir sonuca bakılmadan önce
amendment olarak kaydedildi (`protocol/AMENDMENTS.md`):

1. Claude Haiku 5.5 ve Sonnet 5.5 yalnızca `temperature = 1` kabul ediyor.
2. 300 token'lık cevap bütçesi 186 cevabı kesti. Bu çağrılar 1 024 token ile yeniden soruldu.

**Sayıların okunuşu.**
- **MEASURED** (ölçülen) sayılar gerçek sağlayıcı çağrılarından gelir; maliyet, sağlayıcının bildirdiği
  maliyettir.
- **ESTIMATED** (tahmini) sayılar, ölçülen sayılardan belirtilen bir formülle türetilir.
- **UNKNOWN** (bilinmiyor), kanıtın bir şey söylemediği anlamına gelir.

Aşağıdaki her sayı kaynağıyla birlikte `EVIDENCE_MAP.md` içinde listelenmiştir.

## Kurulum

* **Dokuz aileden 110 kapalı uçlu vaka:** feature tarama, hedef yorumu, politika çatışması, validation yorumu,
  model seçimi, XAI yorumu, eksik kaynak, feature-engineering önerisi ve yüksek sonuçlu kararlar.
* **Doğru cevap** kamuya açık veri seti dokümantasyonundan ya da vakanın içinde yazan bir kuraldan gelir; hiçbir
  zaman bir modelden gelmez. Hiçbir veri satırı kullanılmadı.
* **Ayrım:** 39 vaka baseline'ı ve "çeşitli" konseyi seçmek için kullanıldı; 71 vaka değerlendirme için ayrıldı.
* **Koşullar:**
  * **A** — güçlü tek bir model;
  * **B** — aynı sağlayıcıdan bir konsey: rol prompt'ları (B1) ya da tek modelden üç örnek (B2);
  * **C** — çok sağlayıcılı bir konsey;
  * **D** — hataları ilişkisiz olsun diye seçilmiş bir konsey;
  * **E** — C'nin üç cevabını okuyup karar veren bir yargıç (judge);
  * **F** — yalnızca anlaşmazlıkta ya da yüksek sonuçlu kararda yükselten uyarlanabilir bir yönlendirici.

## Sonuç (MEASURED)

* **Güçlü tek model** (Sonnet 5.5), ayrılmış 71 vakanın **70'ini** doğru cevapladı (0,986).
* **Hiçbir konsey onu geçemedi:**
  * çok sağlayıcılı konsey (C) ve yargıç (E) ona **eşit** kaldı (70/71);
  * rol konseyi, örnekleme konseyi, "çeşitli" konsey ve yönlendirici **69/71** yaptı
    (0,972; Δ −0,014, %95 GA [−0,042, 0]).
* **Önceden kayda geçirilmiş kurallara göre** tüm konsey koşulları **REJECTED_ON_THIS_BENCHMARK** (bu
  benchmark'ta reddedildi).
  - H0 (konsey en iyi tek modeli anlamlı biçimde geçmez) reddedilmedi.
  - H1 (değer zor segmentlerde toplanır) desteklenmedi.
  - H3 (uyarlanabilir yönlendirme daha iyi bir sınır verir) reddedildi.

## Maliyet ve gecikme

| Koşul | Doğruluk | Çağrı / karar | Token / karar | Gecikme sn / karar | Maliyet $ / karar |
|---|---|---|---|---|---|
| A güçlü tek model (Sonnet) | 0,986 | 1 | 432 | 2,31 | 0,00199 |
| A ucuz tek model (Haiku) | 0,986 | 1 | 490 | 1,77 | 0,00013 |
| B1 roller | 0,972 | 3 | 1 786 | 2,43 | 0,00049 |
| B2 örnekleme | 0,972 | 3 | 1 459 | 2,10 | 0,00038 |
| C çok sağlayıcılı | 0,986 | 3 | 1 187 | 2,71 | 0,00212 |
| D çeşitli | 0,972 | 3 | 1 344 | 2,72 | 0,00218 |
| E yargıç | 0,986 | 4 | 1 927 | 5,26 | 0,00490 |
| F yönlendirici | 0,972 | 3,35 | 1 501 | 3,07 | 0,00203 |

* **Maliyet ve çağrı başına gecikme MEASURED'dır.** Maliyet sağlayıcının bildirdiği maliyettir; yerel Qwen
  çağrıları 0'dır.
* **Konsey gecikmesi ESTIMATED'dır.** Üyelerin paralel çalıştığı varsayımıyla, en yavaş üyeye yargıç
  eklenerek hesaplanır.
* **Yargıç (E):** güçlü tek modelle aynı doğrulukta, onun **2,5 katı** maliyet (0,004899 $ / 0,001994 $) ve
  **2,3 katı** gecikme (5,26 sn / 2,31 sn).
* **Yönlendirici (F):** **71 karardan 36'sını** insan incelemesine gönderdi; çünkü kural gereği her yüksek
  sonuçlu vaka yükseltildi.
* **Aynı doğruluğu veren en ucuz yapılandırma:** tek başına Haiku; karar başına maliyeti güçlü tek modelin
  yaklaşık 1/15'i.
* **Deneyin sağlayıcı tarafından bildirilen toplam maliyeti:** 1 506 farklı kayıtlı çağrı için 0,71 $
  (yeniden sorulan 186 çağrı dahil 1 396 üye çağrısı ve 110 yargıç çağrısı). Daha önceki 1,04 $ iç rakamı,
  arşivlenen 300 token'lık turu iki kez saymıştı; arşivin satırları nihai cache'in ilk 1 210 satırıdır.
* **UNKNOWN:**
  - production ağ yolundaki gecikme;
  - prompt önbelleği etkileri;
  - maliyet bildirmeyen sağlayıcıların maliyeti.

## Yorum

70/71 yapan tek bir model, konseye kazanabileceği en fazla bir vaka bırakır. Karar kuralı da "değer yok" ile
"yer yok" arasındaki farkı ayırt edemez. Savunulabilir okuma dardır: *öncü bir modelin zaten doğru cevapladığı
yönetişim sorularında konsey doğruluk eklemedi ve aynı doğruluktaki en ucuz tek modelden daha pahalıya geldi.*
Güçlü tek modele göre ise yalnızca Haiku'dan oluşan B1 ve B2 konseyleri karar başına daha ucuz, ama daha az
doğruydu.

Bu, konseylerin hiçbir zaman işe yaramadığını **göstermez**. Öncü bir modelin yanıldığı sorular hakkında iki
yönde de kanıt yoktur; konseyin değerini kanıtlaması gereken yer de tam orasıdır.

Verinin gerçekten gösterdiği şey, üyelerin nasıl hata yaptığıdır:

* **Aynı model, aynı hatalar.** Sonnet ve Haiku *aynı* tek hatayı yaptı (hata korelasyonu 1,0). İkisini üst
  üste koymak hiçbir şey kazandırmaz.
* **Rol prompt'u modelin hata biçimini değiştirir.**
  * "Temkinli doğrulayıcı" rolü, Claude üyeleri arasındaki tek yanlış alarmları üretti (0,059).
  * "Semantik eleştirmen" rolü, kritik kaçırması sıfır olan tek Claude üyesiydi.
* **Çoğunluk oyu faydalı sinyali çöpe attı.** `feature_screening:29` ve `:34` vakalarında eleştirmen doğru
  cevabı verdi. Her iki vakada da diğer iki rol üyesi onu oyla azınlıkta bıraktı.
* **Kazanç sağlayıcı sayısını değil, ortak hatayı izledi.** Üç üyeli 35 konseyin tamamında kazanç, üyelerin
  *aynı vakada* ne sıklıkla yanıldığını izledi (sıra korelasyonu −0,83). Sağlayıcı sayısıyla ilişkisi çok daha
  zayıftı (−0,18). Bu bir betimlemedir: kombinasyonlar örtüşüyor ve ikinci sağlayıcı çok daha zayıf bir yerel
  modeldi.

## Diğer muhakeme yöntemleri nedir, ne ölçülmedi

| Yöntem | Uygulandı | Bağlandı | Değerlendirme |
|---|---|---|---|
| Konsey (oy) | evet | evet, tavsiye niteliğinde | MEASURED (bu çalışma) |
| Proposer / judge | evet | evet, varsayılan olarak kapalı | yalnızca E koşulu olarak MEASURED |
| Koruyucu azınlık vetolu eleştirmen | hayır | hayır | NOT_RUN |
| CoT / ToT / GoT | evet, birleştirme olarak | evet, yalnızca güven | SIMULATED (mock runner) |
| Self-consistency | hayır | hayır | NOT_RUN |
| ReAct | hayır | hayır | NOT_RUN |
| Reflexion (tek teşhis ve yeniden deneme adımı) | evet | evet, yalnızca API | NOT_RUN |
| Program-of-Thought / kanıt zorunluluğu | evet, kısmi | evet | NOT_RUN |
| MCTS (feature stratejisi) | hayır | hayır | NOT_RUN |
| Jev sınırlı kararlar | evet | evet, varsayılan olarak kapalı | farklı bir benchmark'ta MEASURED |

* **Athena'daki CoT / ToT / GoT, dil modeli muhakemesi değildir.** Bunlar konsey üyelerinin cevapları üzerinde
  sonradan yapılan birleştirmelerdir. Zincir, ağaç ya da graf dönen metinden kurulur ve kendi başına hiçbir
  model çağrısı yapmaz. Tek etkisi ×1,15'lik bir güven artışıdır; bu artış varsayılan oy stratejisinde yalnızca
  eşitliği bozar. Bu nedenle bu yöntemler güven / eşitlik bozma davranışı olarak etiketlenir ve doğrulukları
  hakkında bir iddiada bulunulmaz.
  Model çağrılarını düzenleyen bir muhakeme yöntemi olarak CoT, ToT ve GoT ise ayrı bir konudur. Bu yöntemler bu
  repository'deki Study A ve A2'de, sınırlı AutoML kararları üzerinde ölçüldü ([reasoning topology](../../reasoning-topology/)); bu vaka
  setinde ölçülmedi.
* **Jev** ayrı bir karar korpusunda ölçüldü (`notebooks/01_routing_and_jev.ipynb`). Tek bir karar ailesinde
  tipli semantik bağlam doğruluğu 0,578'den 0,733'e çıkardı; ancak %95 aralıkları örtüştüğü için kazanç
  kanıtlanmış değildir. Sağlayıcı fiyat bildirmediği için maliyeti UNKNOWN'dır.

## Sınırlılıklar

* **Tavan.** Tek model 70/71 yaptığı için benchmark bir iyileşme gösteremez.
* **Sağlayıcılar.** Yalnızca iki sağlayıcı ailesine erişilebildi. İkincisi, yerel bir 7B model, çok daha düşük
  skor aldı (0,620); onu eklemek çoğunlukla hata ekledi.
* **Ürün değil, harness.** Harness modelleri doğrudan çağırdı. Athena'nın konsey endpoint'i, kanıt doğrulayıcısı
  ve tenant bağlamı kullanılmadı; bu yüzden doğrulayıcı uyumu ve organizasyon bağlamı kullanımı `NOT_MEASURED`.
* **Çıkarım değil, betimleme.** 35 kombinasyon birbiriyle örtüşüyor ve bağımsız örnek değil.
* **Tek yapılandırma.** Tek bir sıcaklık (sağlayıcının zorunlu kıldığı) ve tek bir prompt ailesi.
* **Yazarlık.** Vakaların yazarı aynı zamanda harness'ın yazarıdır. Tek modelin tek hatasının
  (`feature_screening:29`) referans cevabı tartışmaya açıktır.

## Sonraki hipotezler (bulgu değildir)

1. **Önce boşluk (headroom).** Öncü bir tek modelin *yanıldığı için* seçilmiş vakalarda bir konsey yardımcı
   olabilir. Bir sonraki çalışma önce kalibrasyonda en az %15 tek model hatası göstermelidir; aksi halde
   `NOT_RUN — CEILING` olarak durdurulur.
2. **Koruyucu azınlık vetosu.** Bir veto kuralı (kalibre edilmiş bir üye kritik risk işaretlerse karar
   yükseltilir) çoğunluk oyunun çöpe attığı itirazı koruyabilir. Test edilmedi; önce ön kayda geçirilecek.
3. **Karakteristik çeşitlilik kanıtlanmadı.** Yalnızca üyelerin hataları hedef görevde ölçülebilir biçimde
   ilişkisizse *ve* en güçlü üye tavanın altındaysa önemli olabilir.

Bunların her biri ve yukarıdaki tablodaki test edilmemiş her yöntem `RESEARCH_PLANNED` olarak kaydedildi. Her
planda hipotez, baseline, görev ailesi, metrik, bütçe, durdurma kuralı ve production kabul kapısı yer alır
(`METHODOLOGY.md`). Hiçbiri ürün yeteneği olarak sunulmaz.

## Athena bugün ne yapıyor

Athena varsayılan yolda güçlü tek bir model, deterministik kontroller ve kanıt doğrulayıcısını kullanır. Leakage
ya da inandırıcı olmayan bir skor gibi bir şey ters göründüğünde Athena sessizce karar vermez; **uyarır** ve
inceleme ister. Konsey bir ürün iddiası değildir.

*Ön kayıt, amendment'lar, ayrıştırılmış model cevapları (ham çıktılar olmadan), yargıç kaydı, analiz harness'ı
ve donmuş kanıtı yeniden okuyan sekiz notebook bu repository'dedir. Analiz, yayımlanan ham olmayan cevaplardan
`evidence/council/results.json` dosyasını birebir yeniden üretir (`REPRODUCIBILITY.md`).*
