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

## Gun 4 - SQLite Veritabani

Bugun RAG projesinin yerel veri katmani icin SQLite kullanildi.

SQLite'in projedeki gorevi:

- Dokuman parcalarini saklamak
- Her parcanin kaynak dosya adini tutmak
- Ileride embedding vektorlerini saklamak
- Retrieval asamasinda kayitlari tekrar okumak

Olusturulan tablo:

documents

Alanlar:

- id: Otomatik benzersiz kayit numarasi
- source: Dokumanin geldigi kaynak dosya
- chunk_index: Dokuman icindeki parca sirasi
- chunk_text: Asil dokuman parcasi
- embedding: Ileride embedding vektorunun saklanacagi alan
- created_at: Kayit tarihi

Bugun yapilan demo:

1. storage/rag.db olusturuldu.
2. documents tablosu kuruldu.
3. Ornek dokuman parcalari tabloya eklendi.
4. Kayitlar SQLite'tan tekrar okundu.

Gun 4 ciktisi:

- src/db.py eklendi.
- src/sqlite_demo.py eklendi.
- SQLite ile veri yazma ve okuma test edildi.

## Gun 5 - Dokuman Seti ve Dosya Okuma

Bugun RAG projesi icin ilk gercek dokuman seti hazirlandi.

Eklenen dokumanlar:

- rag_notes.txt
- foundry_local_notes.txt
- sqlite_notes.txt
- project_overview.txt

Bu adimin amaci, dokumanlari artik Python listesi icinde degil, gercek dosyalar olarak saklamaktir.

Document loader'in gorevi:

1. data/documents klasorunu bulmak
2. .txt dosyalarini okumak
3. Her dokumani source ve text bilgisiyle listelemek
4. Ileride chunking ve embedding islemlerine veri saglamak

Neden source bilgisi tutuyoruz?

Cunku RAG sisteminde cevap verirken bilginin hangi dokumandan geldigini bilmek isteriz. Ileride kaynak gostermek icin source alani onemli olacak.

Gun 5 ciktisi:

- data/documents icine ornek .txt dokumanlar eklendi.
- src/document_loader.py eklendi.
- src/document_loader_demo.py eklendi.
- Python ile dokuman okuma test edildi.


## Gun 6 - Chunking

Bugun dokumanlari kucuk parcalara bolme mantigi ogrenildi.

Chunking, uzun dokumanlari daha kucuk ve aranabilir parcalara ayirma islemidir.

Neden chunking kullaniyoruz?

- Uzun dokumanin tamamini modele vermek verimsizdir.
- Kullanici sorusu genellikle dokumanin kucuk bir bolumuyle ilgilidir.
- Embedding aramasinda kucuk ve net parcalar daha iyi sonuc verir.
- Ileride cevaplarda kaynak gostermek daha kolay olur.

Bugun yapilanlar:

1. data/documents icindeki dokumanlar okundu.
2. Her dokuman paragraflara ayrildi.
3. Her paragraf bir chunk olarak hazirlandi.
4. Her chunk icin source, chunk_index ve chunk_text bilgileri olusturuldu.

Gun 6 ciktisi:

- src/chunker.py eklendi.
- src/chunking_demo.py eklendi.
- Dokumanlari chunk'lara bolme demosu calisti.

## Gun 7 - Chunk Embedding Uretimi

Bugun gercek dokuman chunk'lari icin embedding uretildi.

Onceki gunlerde yapilanlar:

- Gun 5: Dokumanlar data/documents klasorunden okundu.
- Gun 6: Dokumanlar chunk'lara bolundu.
- Gun 7: Her chunk embedding vektorune cevrildi.

Bu adimin amaci, RAG sisteminin retrieval asamasinda kullanacagi sayisal temsilleri hazirlamaktir.

Embedding neden gerekli?

Bilgisayar metinlerin anlamca yakin olup olmadigini dogrudan anlayamaz. Embedding, metinleri sayisal vektor haline getirir. Daha sonra kullanici sorusunun embedding'i ile dokuman chunk embedding'leri karsilastirilerek en alakali chunk'lar bulunur.

Bugun yapilanlar:

1. src/embedder.py eklendi.
2. Foundry Local embedding modeli ayri bir yardimci sinif icinde kullanildi.
3. Dokumanlar okundu.
4. Dokumanlar chunk'lara bolundu.
5. Her chunk icin embedding uretildi.
6. Embedding boyutu kontrol edildi.
7. Model alias problemi cozuldu. Calisan ana alias: qwen3-embedding-0.6b

Gun 7 sonuc:

- 4 dokuman okundu.
- 16 chunk uretildi.
- 16 chunk icin embedding uretildi.
- Her embedding'in boyutu 1024 olarak dogrulandi.

Gun 7 ciktisi:

- src/embedder.py eklendi.
- src/chunk_embedding_demo.py eklendi.
- Gercek dokuman chunk'lari icin embedding uretimi test edildi.


## Day 8 — SQLite Ingestion Pipeline

### Goal

Combine the document loader, chunker, embedding model, and SQLite database into a complete ingestion pipeline.

### What was implemented

- Added `insert_documents()` to `src/db.py`
- Used `executemany()` to insert multiple chunks with one database transaction
- Added `src/ingest.py`
- Added `src/ingest_demo.py`
- Loaded real text documents from `data/documents/`
- Split the documents into paragraph-based chunks
- Generated a local embedding for every chunk
- Converted embedding vectors into JSON strings
- Stored chunk metadata, text, and embeddings in SQLite
- Read the records back from SQLite
- Verified that the number of stored records matched the generated chunk count
- Verified that a stored embedding could be restored with `json.loads()`

### Test result

- Documents loaded: 4
- Chunks generated: 16
- Records inserted: 16
- Records read from SQLite: 16
- Embedding dimensions: 1024

### Key learning

An ingestion pipeline prepares raw documents for retrieval. It transforms documents into searchable chunks and persists their vector representations so embeddings do not need to be recomputed for every user question.

Embedding vectors are stored as JSON text because the current SQLite schema uses a `TEXT` column. During retrieval, the JSON string can be converted back into a Python list using `json.loads()`.

The database is reset only after embedding generation succeeds. This prevents an embedding error from deleting the previously working database unnecessarily.

### Next step

Implement semantic retrieval by embedding a user query, loading stored embeddings from SQLite, calculating cosine similarity, and returning the top matching chunks.