from elasticsearch import Elasticsearch
import matplotlib.pyplot as plt
import pandas as pd

# Conexión local
es = Elasticsearch("http://localhost:9200", verify_certs=False)

# Buscar datos
res = es.search(index="iris", size=150, query={"match_all": {}})
docs = [hit["_source"] for hit in res["hits"]["hits"]]

# Convertir a DataFrame
df = pd.DataFrame(docs)

# Graficar sepal_length por especie
df.groupby("species")["sepal_length"].mean().plot(kind="bar", title="Promedio Sepal Length por especie")
plt.ylabel("cm")
plt.tight_layout()
plt.savefig("docs/grafico_iris.png")
