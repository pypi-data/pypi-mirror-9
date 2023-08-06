import gossip

step_hook_group = gossip.create_group("step")
step_hook_group.set_strict()

step_start = gossip.define('slash.step_start')
step_success = gossip.define('slash.step_success')
step_error = gossip.define('slash.step_error')
step_end = gossip.define('slash.step_end')
