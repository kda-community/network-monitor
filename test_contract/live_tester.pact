(namespace "free")

(module live-tester GOV
  @doc "Simple module to test that the chain is still alive"

  (defcap GOV ()
    (enforce false "Not upgradable"))

    (defschema test-tx
      result: bool)

    (deftable test-tx-table:{test-tx})

    (defun do-test ()
      @doc "Record a test transaction"
      (insert test-tx-table (tx-hash) {'result:true}))

    (defun is-test-ok:bool ( reqKey:string )
      @doc "Check that the transaction was properly recorded"
      (with-default-read test-tx-table reqKey {'result:false} {'result:=result}
        result))
)

(create-table test-tx-table)