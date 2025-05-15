import logging
from pprint import pformat
from typing import Any, Collection, Dict, List, Literal, Mapping, Union

import vizro.models as vm
from dash import Input, Output, callback, html, no_update
from dash_auth.group_protection import CheckType, protected
from vizro.models._models_utils import _log_call

logger = logging.getLogger(__name__)


class ProtectedAction(vm.Action):
    """Action to be inserted into `actions` of relevant component that uses `dash-auth` to enforce authentification and
    group permissions.

    Args:
        function (CapturedCallable): Action function.
        inputs (list[_DotSeparatedStr]): List of inputs provided to the action function, each specified as
            `<component_id>.<property>`. Defaults to `[]`.
        outputs (Union[list[_DotSeparatedStr], dict[str, _DotSeparatedStr]]): List or dictionary of outputs modified by
            the action function, where each output needs to be specified as `<component_id>.<property>`.
            Defaults to `[]`.
        groups (list[str]): List of authorized user groups. If no groups are passed, the decorator will only check
            whether the user is authenticated.
        groups_key (str): Groups key in the user data saved in the Flask session e.g.
            ``session["user"] == {"email": "a.b@mail.com", "groups": ["admin"]}``
        groups_str_split (str): Used to split groups if provided as a string.
        check_type (Literal["one_of", "all_of", "none_of"]): Type of check to perform. Either "one_of", "all_of" or
            "none_of".
    """
    # TODO: Commented out because could not add_type properly otherwise. type is now "action"
    # type: Literal["protected_action"] = "protected_action"

    groups: list[str] | None = None
    groups_key: str = "groups"
    groups_str_split: str = None
    check_type: CheckType = "one_of"
    unauthenticated_modal_id: str | None = None
    missing_permission_modal_id: str | None = None

    @property
    def _transformed_outputs(self) -> list[Output] | dict[str, Output]:
        """Creates Dash Output objects from string specifications in self.outputs.

        Converts self.outputs (list of strings or dictionary of strings where each string is in the format
        '<component_id>.<property>') and converts into actual Dash Output objects.
        For example, ['my_graph.figure'] becomes [Output('my_graph', 'figure', allow_duplicate=True)].

        Returns:
            Union[list[Output], dict[str, Output]]: A list of Output objects if self.outputs is a list of strings,
            or a dictionary mapping keys to Output objects if self.outputs is a dictionary of strings.
        """

        def _transform_output(output):
            return Output(*output.split("."), allow_duplicate=True)

        self._n_outputs = len(self.outputs)
        outputs = self.outputs
        if self.unauthenticated_modal_id is not None:
            outputs.append(f"{self.unauthenticated_modal_id}.is_open")

        if self.missing_permission_modal_id is not None:
            outputs.append(f"{self.missing_permission_modal_id}.is_open")

        if isinstance(outputs, list):
            callback_outputs = [_transform_output(output) for output in outputs]

            # Need to use a single Output in the @callback decorator rather than a single element list for the case
            # of a single output. This means the action function can return a single value (e.g. "text") rather than a
            # single element list (e.g. ["text"]).
            if len(callback_outputs) == 1:
                callback_outputs = callback_outputs[0]

            return callback_outputs

        return {output_name: _transform_output(output) for output_name, output in outputs.items()}

    def _action_callback_function(
        self,
        inputs: Union[Dict[str, Any], List[Any]],
        outputs: Union[Dict[str, Output], List[Output], Output, None],
    ) -> Any:
        logger.debug("===== Running action with id %s, function %s =====", self.id, self.function._function.__name__)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Action inputs:\n%s", pformat(inputs, depth=3, width=200))
            logger.debug("Action outputs:\n%s", pformat(outputs, width=200))

        if isinstance(inputs, Mapping):
            return_value = self.function(**inputs)
        else:
            return_value = self.function(*inputs)

        if self.unauthenticated_modal_id is not None and self.missing_permission_modal_id is not None:
            if not isinstance(return_value, Collection):
                return_value = [return_value]
            return_value.extend([False, False])
        elif self.unauthenticated_modal_id is not None or self.missing_permission_modal_id is not None:
            if not isinstance(return_value, Collection):
                return_value = [return_value]
            return_value.extend([False])

        # Delegate all handling of the return_value and mapping to appropriate outputs to Dash - we don't modify
        # return_value to reshape it in any way. All we do is do some error checking to raise clearer error messages.
        if not outputs:
            if return_value is not None:
                raise ValueError("Action function has returned a value but the action has no defined outputs.")
        elif isinstance(outputs, dict):
            if not isinstance(return_value, Mapping):
                raise ValueError(
                    "Action function has not returned a dictionary-like object "
                    "but the action's defined outputs are a dictionary."
                )
            if set(outputs) != set(return_value):
                raise ValueError(
                    f"Keys of action's returned value {set(return_value) or {}} "
                    f"do not match the action's defined outputs {set(outputs) or {}})."
                )
        elif isinstance(outputs, list):
            if not isinstance(return_value, Collection):
                raise ValueError(
                    "Action function has not returned a list-like object but the action's defined outputs are a list."
                )
            if len(return_value) != len(outputs):
                raise ValueError(
                    f"Number of action's returned elements {len(return_value)} does not match the number"
                    f" of action's defined outputs {len(outputs)}."
                )

        # If no error has been raised then the return_value is good and is returned as it is.
        # This could be a list of outputs, dictionary of outputs or any single value including None.
        return return_value

    @_log_call
    def build(self) -> html.Div:
        """Builds a callback for the Action model and returns required components for the callback.

        Returns:
            Div containing a list of required components (e.g. dcc.Download) for the Action model

        """
        # TODO: after sorting out model manager and pre-build order, lots of this should probably move to happen
        #  some time before the build phase.
        external_callback_inputs = self._transformed_inputs
        external_callback_outputs = self._transformed_outputs

        callback_inputs = {
            "external": external_callback_inputs,
            "internal": {"trigger": Input({"type": "action_trigger", "action_name": self.id}, "data")},
        }
        callback_outputs: dict[str, list[Output] | dict[str, Output]] = {
            "internal": {"action_finished": Output("action_finished", "data", allow_duplicate=True)},
        }

        # If there are no outputs then we don't want the external part of callback_outputs to exist at all.
        # This allows the action function to return None and match correctly on to the callback_outputs dictionary
        # The (probably better) alternative to this would be just to define a dummy output for all such functions
        # so that the external key always exists.
        # Note that it's still possible to explicitly return None as a value when an output is specified.
        if external_callback_outputs:
            callback_outputs["external"] = external_callback_outputs

        logger.debug(
            "===== Building callback for Action with id %s, function %s =====",
            self.id,
            self._action_name,
        )
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Callback inputs:\n%s", pformat(callback_inputs["external"], width=200))
            logger.debug("Callback outputs:\n%s", pformat(callback_outputs.get("external"), width=200))

        @callback(output=callback_outputs, inputs=callback_inputs, prevent_initial_call=True)
        def callback_wrapper(external: list[Any] | dict[str, Any], internal: dict[str, Any]) -> dict[str, Any]:
            unallowed_output = (no_update, ) * self._n_outputs

            unauthenticated_output, missing_permissions_output = None, None
            if self.unauthenticated_modal_id is not None and self.missing_permission_modal_id is not None:
                unauthenticated_output = unallowed_output + (True, False)
                missing_permissions_output = unallowed_output + (False, True)
            elif self.unauthenticated_modal_id is not None:
                unauthenticated_output = unallowed_output + (True, )
            elif self.missing_permission_modal_id is not None:
                missing_permissions_output = unallowed_output + (True, )

            return_value = protected(
                unauthenticated_output=unauthenticated_output,
                missing_permissions_output=missing_permissions_output,
                groups=self.groups,
                groups_key=self.groups_key,
                groups_str_split=self.groups_str_split,
                check_type=self.check_type,
            )(self._action_callback_function)(inputs=external, outputs=callback_outputs.get("external"))

            if "external" in callback_outputs:
                return {"internal": {"action_finished": None}, "external": return_value}
            return {"internal": {"action_finished": None}}

        return html.Div(id=f"{self.id}_action_model_components_div", children=self._dash_components, hidden=True)
