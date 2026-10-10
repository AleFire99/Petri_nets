import { setup } from 'xstate';

/** Parallel (orthogonal) regions: independent text styles. Design: docs/fsm/parallel.md. */
export const textStyle = setup({
  types: {
    events: {} as { type: 'toggle_bold' } | { type: 'toggle_italic' } | { type: 'toggle_underline' },
  },
}).createMachine({
  id: 'textStyle',
  type: 'parallel',
  states: {
    bold: {
      initial: 'bold_off',
      states: {
        bold_off: { on: { toggle_bold: { target: 'bold_on' } } },
        bold_on: { tags: ['BOLD'], on: { toggle_bold: { target: 'bold_off' } } },
      },
    },
    italic: {
      initial: 'italic_off',
      states: {
        italic_off: { on: { toggle_italic: { target: 'italic_on' } } },
        italic_on: { tags: ['ITALIC'], on: { toggle_italic: { target: 'italic_off' } } },
      },
    },
    underline: {
      initial: 'underline_off',
      states: {
        underline_off: { on: { toggle_underline: { target: 'underline_on' } } },
        underline_on: { tags: ['UNDERLINE'], on: { toggle_underline: { target: 'underline_off' } } },
      },
    },
  },
});
