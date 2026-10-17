import { useState } from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import { Button, Modal } from "../src/components/ui";
import { DependencyList } from "../src/components/Evidence";

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

it("identifies shortened relationship evidence without marking ordinary references as previews", () => {
  const { rerender } = render(
    <DependencyList
      items={[{
        source_file: "src/request.ts",
        reference: "builder.map(...",
        resolved: false,
        preview_truncated_fields: ["reference"],
        reference_length: 500,
      }]}
    />,
  );
  expect(screen.getByText("Relationship preview")).toBeInTheDocument();
  expect(screen.getByText("Unresolved")).toBeInTheDocument();
  rerender(<DependencyList items={[{ source_file: "src/request.ts", reference: "verify", resolved: true }]} />);
  expect(screen.queryByText("Relationship preview")).not.toBeInTheDocument();
  expect(screen.getByText("Resolved")).toBeInTheDocument();
});

it("focuses an enabled editor control and traps keyboard navigation inside the dialog", async () => {
  render(
    <>
      <Button>Background action</Button>
      <Modal title="Edit memory" onClose={() => undefined}>
        <label htmlFor="category">Category</label>
        <select id="category" disabled><option>Decision</option></select>
        <label htmlFor="finding">Finding</label>
        <textarea id="finding" />
        <Button>Save changes</Button>
      </Modal>
    </>,
  );
  const finding = screen.getByRole("textbox", { name: "Finding" });
  expect(finding).toHaveFocus();
  await userEvent.tab();
  expect(screen.getByRole("button", { name: "Save changes" })).toHaveFocus();
  await userEvent.tab();
  expect(screen.getByRole("button", { name: "Close dialog" })).toHaveFocus();
  await userEvent.tab({ shift: true });
  expect(screen.getByRole("button", { name: "Save changes" })).toHaveFocus();
  // Scripted focus changes must not let the next Tab navigate the background.
  screen.getByRole("button", { name: "Background action" }).focus();
  await userEvent.tab();
  expect(screen.getByRole("button", { name: "Close dialog" })).toHaveFocus();
});
