HELLO

TEST HELLO

BACKPORT TEST

BACKPORT TEST AGAIN

#  ref: ${{ github.event.pull_request.head.sha }} use this insted of "refs/pull/${{ github.event.number }}/merge" -> raději volat fixed sha commit, menší riziko prohození kodu
# or Checkout refs/pull/${{ github.event.number }}/merge and then verify HEAD^ equals github.event.pull_request.head.sha
