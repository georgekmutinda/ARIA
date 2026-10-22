import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

rng = np.random.default_rng(seed=42)
N = 200

df = pd.DataFrame({
    "query_id" : [f"q_{i:04d}" for i in range(N)], 
    "query" : rng.choice(["What is RAG?", "Explain embeddings.", "How does chunking work?", "What is a vector DB", "Explain fine tuning"], size = N),
    "retrieved_chunks": rng.integers(1, 6, size =N ),
    "retrieval_score" :rng.uniform(0.3, 1.0, size =N),
    "faithfulness" : rng.uniform(0.4, 1.0, size = N ).round(3),
    "answer_relevance": rng.uniform(0.2, 1.0,  size =N).round(3),
    "latency_ms": rng.integers(120, 2500, size =N),
    "model":rng.choice(["llama", "phi", "gpt"],  size = N),
    "source_type" : rng.choice(["pdf", "web", "database"], size = N),
    })
null_indices = rng.choice(N, size = 15, replace =False)
df.loc[null_indices,"faithfulness"] =np.nan
df.loc[null_indices, "latency_ms"]=np.nan
df.to_csv("random_rag_eval_data.csv", index=False)



print(f"created dataset: {df.shape} ,{df.dtypes}")
print(df.head())

nulls = df["latency_ms"].isnull().sum()
print(f"This are the nulls in the latency column {nulls}")
nulls_percentage = df.isnull().sum() / len(df) * 100
print("Nulls percentage before filling ",nulls_percentage)

#handling missing data
df["faithfulness"]= df["faithfulness"].fillna(df["faithfulness"].median())
df["latency_ms"]=df["latency_ms"].fillna(df["latency_ms"].median())
#print("Nulls after filling them", df["faithfulness"],df["latency_ms"]) this is costly to do, so the shortcut just check the null count.
null_count = df.isnull().sum()

#filter
df_filtered = df[(df["retrieval_score"] > 0.6) & (df["latency_ms"] < 1200)]
print( "This is the filtered Dataset..........", df_filtered)
#Once the data is filtered every single downstream operation must explicitly reference that new variable created from filtering.

#enrich filtered dataset
df_filtered["quality_score"] =( df_filtered["retrieval_score" ] * 0.4 + df_filtered["faithfulness" ] * 0.4 + df_filtered["answer_relevance" ] * 0.2).copy() # the copy allows you to add a column later to the filtered data, without it python is confused where do i add the data as it is not stored just the view

#aggregate metrics on filtered dataset
model_stats = df_filtered.groupby("model").agg(
    mean_quality_score =("quality_score", "mean"),
     mean_latency = ("latency_ms", "mean"),
     count = ("quality_score","count")
    
).sort_values(by="mean_quality_score", ascending=False)

#scaling
scaler = MinMaxScaler()
df_filtered["scaled_quality_score"] = scaler.fit_transform(df_filtered[["quality_score"]])
df_filtered["scaled_latency_ms"]= scaler.fit_transform(df_filtered[["latency_ms"]])

#export the data
df_filtered.to_csv("cleaned_dataset.csv", index=False)
print(model_stats)
model_stats.to_csv("model_stats.csv", index=True)
""""
print(df.tail())







print(df)
print(filter)
"""
