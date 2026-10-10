import { setup } from 'xstate';

/** Hierarchical FSM: `power_off` declared once on the parent. Design: fsm/docs/hierarchical.md. */
export const mediaPlayer = setup({
  types: {
    events: {} as
      | { type: 'power_on' }
      | { type: 'power_off' }
      | { type: 'play' }
      | { type: 'pause' }
      | { type: 'stop' },
  },
}).createMachine({
  /** @xstate-layout N4IgpgJg5mDOIC5QFtIEsCGAFANhgnmAE4B0A9gGYUDEADmQO7ED6ZAdgNoAMAuoqPVhoALmnb8QAD0QBGAGwBOElxUqAzAoAcAVjnauAFgMAaEPkQAmbQZLbNatV00WDFuTI8B2AL7fTqCExcAmJyNjpGFkoKbj4kEEERMTYJaQR5JVV1LV19I1NzBAtDZXtHOU81Zws1a19-dGw8QlJ2ElhhMlpaSDpm2IlE0XF4tLlNGysVGQUuDQsFOwLLLhlbLN1PFxk5g3qQAKDm0LbaZrQ2KDoMAFdYMAH4oeTUxHHJ-VXZ+cXNZYQjGplFlPDJPBUFJ4FHJ9ocmiFWmwSGcCBcrh0uo8BGQhMMUqM3tCSDJdG5FoZtGo3P8SWssoZ5JouBYLD4-AdGsEWmFkbd7hA+gQsQkcUkRqA0gZ3CRZnI3DVDNDHCYzIgqRYSFMVHJXFLDBZYZzjojeXdehjaMLnuKpIgpWtZfLlUrDDSFECDPIKsVNPYDNo2ey2GQIHAJHCucRBqK8a8EABaOT-eM1GUKdMZzPpzSGwLw7nRaO4l4EgEWf4WHbEuQ1gxzFkWX1g3NHBFhIti-ESyyaOQyrhyuxqGbD6mqhByD0Z3SackONwt-MnJEWnoQDux0vaAOaz4kriUnXWN1AhRerZOP0BxeRk0o-Bojcl7sITQedYqBuUysGBT-VxKOS2pbNYb5sg0ea3jytB8pAT42mkDg2I6Q4jjIY6FFS2i7qoOouHI+q+L4QA */
  id: 'mediaPlayer',
  initial: 'off',
  states: {
    off: { on: { power_on: { target: 'on' } } },
    on: {
      initial: 'stopped',
      on: { power_off: { target: 'off' } },
      states: {
        stopped: { on: { play: { target: 'playing' } } },
        playing: { tags: ['AUDIO'], on: { pause: { target: 'paused' }, stop: { target: 'stopped' } } },
        paused: { on: { play: { target: 'playing' }, stop: { target: 'stopped' } } },
      },
    },
  },
});
