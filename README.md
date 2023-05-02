# Python Load & Stress Tests

## Build

```bash
docker build -t load-tester .
```

## Run

```bash
docker run -it \
-e METHOD=<method> \
-e URL=<url> \
-e AUTH_HEADER=<auth_header> \
-e DATA=<data> \
-e NUM_USERS=<num_users> \
-e NUM_REQUESTS=<num_requests> \
load-tester
```
