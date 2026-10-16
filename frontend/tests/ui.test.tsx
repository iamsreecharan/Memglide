import { useState } from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import { Button, Modal } from "../src/components/ui";

it("keeps a busy action disabled even when its ordinary disabled condition is false", async () => {
  const action = vi.fn();
  render(
    <Button disabled={false} busy onClick={action}>
      Save memory
    </Button>,
  );
  const button = screen.getByRole("button", { name: "Save memory" });
  expect(button).toBeDisabled();
  expect(button).toHaveAttribute("aria-busy", "true");
  await userEvent.click(button);
  expect(action).not.toHaveBeenCalled();
});

it("keeps modal keyboard focus stable across input rerenders and handles Escape", async () => {
  const closed = vi.fn();
  function Form() {
    const [value, setValue] = useState("");
    return (
      <Modal title="Add repository" onClose={() => closed()}>
        <label htmlFor="path">Repository path</label>
        <input
          id="path"
          value={value}
          onChange={(event) => setValue(event.target.value)}
        />
        <Button>Register</Button>
      </Modal>
    );
  }
  render(<Form />);
  const input = screen.getByRole("textbox", { name: "Repository path" });
  expect(input).toHaveFocus();
  await userEvent.keyboard("/approved/repository");
  expect(input).toHaveValue("/approved/repository");
  expect(input).toHaveFocus();
  await userEvent.keyboard("{Escape}");
  expect(closed).toHaveBeenCalledOnce();
});
