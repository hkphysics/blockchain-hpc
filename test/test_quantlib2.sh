curl -H "Content-Type: application/json" \
     --request POST \
     --data '{
"VanillaOptionBase": {"resource_name":"VanillaOption","payoff":{"resource_name":"PlainVanillaPayoff","type":-1,"strike":40.0},"exercise":{"resource_name":"EuropeanExercise","date":{"resource_name":"Date","d":4,"m":1,"y":2022}}}
}' http://localhost:8002/test1
