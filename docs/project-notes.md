# Project Notes

## Gun 1 - Proje Baslangici

Bugun GitHub uzerinde proje reposu olusturuldu ve yerel gelistirme ortami hazirlandi.

## Proje Amaci

Bu projenin amaci, Microsoft Foundry Local kullanarak yerelde calisan bir RAG tabanli dokuman soru-cevap asistani gelistirmektir.

## RAG Mantigi

RAG = Retrieve + Augment + Generate

- Retrieve: Kullanici sorusuyla ilgili dokuman parcalarini bul.
- Augment: Bulunan parcalari modele context olarak ver.
- Generate: Modelden bu context'e dayali cevap uret.

## Genel Akis

1. Kullanici soru sorar.
2. Soru embedding'e cevrilir.
3. SQLite icindeki dokuman embedding'leriyle karsilastirilir.
4. En alakali dokuman parcalari secilir.
5. Bu parcalar prompt'a eklenir.
6. Foundry Local uzerindeki model cevap uretir.
7. Cevap kullaniciya gosterilir.

## Gun 1 Ciktisi

- Repository hazir.
- Proje klasor yapisi olustu.
- Ilk Python dosyasi yazildi.
- README eklendi.

## Gun 2 - Python Ortami ve Foundry Local Testi

Bugun projeye ozel Python sanal ortami olusturuldu ve Foundry Local SDK ile basit bir model testi yapildi.

Bu adimin amaci, ileride RAG pipeline'inin Generate asamasinda kullanacagimiz yerel LLM'in bilgisayarda calistigini dogrulamaktir.

Test akisi:

1. Foundry Local baslatildi.
2. Model bilgisi alindi.
3. Model indirildi veya cache'den kontrol edildi.
4. Model yuklendi.
5. Modele basit bir soru soruldu.
6. Model cevap uretti.
7. Model kapatildi.

Sonuc:

Foundry Local testi basariyla tamamlandi.


## Gun 3 - Embedding ve Benzerlik Aramasi

Bugun RAG sisteminin Retrieve asamasinin temel mantigi ogrenildi.

Embedding, bir metni sayisal vektore cevirmektir. Bu sayede bilgisayar iki metnin anlamca birbirine yakin olup olmadigini hesaplayabilir.

Bugun yapilan demo:

1. Ornek dokumanlar belirlendi.
2. Her dokuman embedding'e cevrildi.
3. Kullanici sorusu embedding'e cevrildi.
4. Soru embedding'i ile dokuman embedding'leri cosine similarity ile karsilastirildi.
5. En yuksek skora sahip dokuman en alakali sonuc olarak secildi.

Sonuc:

Sistem, "How does RAG make answers more reliable?" sorusu icin en alakali dokuman olarak RAG'in hallucination'i azalttigini anlatan dokumani secti.

Gun 3 ciktisi:

- src/embedding_demo.py eklendi.
- Foundry Local embedding modeli test edildi.
- Cosine similarity fonksiyonu yazildi.
- Soruya en alakali dokumani bulma mantigi calisti.